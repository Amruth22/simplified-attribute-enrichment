"""
Core enrichment logic for the Simplified Attribute Enrichment service
"""
import asyncio
import json
import logging
import time
import pandas as pd
from typing import Dict, List, Any, Optional

# Import models
from models import TokenStats, token_stats

# Import services
from services import generate_gemini_response, search_part_images_async, process_product_images

# Import templates
from templates import get_template

# Import utilities
from utils import get_debug_prefix, extract_json_from_response, get_task_id, get_output_path

# Import configuration
from config import settings

# Configure logging
logger = logging.getLogger("attribute_enricher.enrichment")

# -------------------- Single Product Enrichment --------------------

async def enrich_product_data(
    mpn: str, 
    manufacturer: Optional[str] = None, 
    category: Optional[str] = None, 
    subcategory: Optional[str] = None, 
    attributes_to_extract: Optional[List[str]] = None, 
    include_images: bool = True, 
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main function to enrich product data with attributes and images
    
    Args:
        mpn: Manufacturer part number
        manufacturer: Manufacturer name
        category: Product category
        subcategory: Product subcategory
        attributes_to_extract: List of attributes to extract
        include_images: Whether to include images in the response
        request_id: Request ID for logging
        
    Returns:
        Dict: Enriched product data
    """
    debug_prefix = get_debug_prefix(request_id)
    start_time = time.time()

    logger.info(f"{debug_prefix}Enriching data for MPN: {mpn}, Manufacturer: {manufacturer}")

    # Default response structure
    response = {
        "mpn": mpn,
        "manufacturer": manufacturer,
        "category": category,
        "subcategory": subcategory,
        "image_url": None,
        "attributes": {},
        "processing_time_seconds": 0,
        "confidence": "LOW",
        "raw_gemini_response": None,
        "requested_attributes": [],
        "token_data": {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "cost_inr": 0
        }
    }

    # Form the category & subcategory combination
    cat_subcat = f"{category},{subcategory}" if category and subcategory else None

    # Get the appropriate template
    template = get_template(category or "Electrical")

    # Get attribute list from taxonomy (implementation omitted for brevity)
    # In a real implementation, this would load from the taxonomy file
    attr_list_from_taxonomy = []
    
    # Use provided attributes or fall back to taxonomy
    final_attributes_to_extract = attributes_to_extract or attr_list_from_taxonomy
    response["requested_attributes"] = final_attributes_to_extract

    # Set up tasks for concurrent execution
    tasks = []

    # Task 1: Image search (if requested)
    if include_images:
        image_search_task = search_part_images_async(mpn, supplier=manufacturer, request_id=request_id)
        tasks.append(("image_search", image_search_task))

    # Task 2: Attribute extraction
    if final_attributes_to_extract:
        # Create a data row for the template
        data_row = {
            'mfg_part_number': mpn,
            'manufacturer_name': manufacturer,
            'cat_subcat': cat_subcat
        }

        # Generate the prompt using the template
        prompt = template.generate_prompt(data_row, final_attributes_to_extract)
        logger.info(f"{debug_prefix}Generated prompt using {template.__class__.__name__}")

        # Generate response from Gemini
        attribute_task = generate_gemini_response(prompt, request_id)
        tasks.append(("attribute_extraction", attribute_task))

    # Execute all tasks concurrently
    if tasks:
        results = {}
        for name, task in tasks:
            try:
                result = await task
                results[name] = result
            except Exception as e:
                logger.error(f"{debug_prefix}Error in {name} task: {str(e)}")
                results[name] = None

        # Process image search results
        if "image_search" in results and results["image_search"]:
            images = results["image_search"]
            if images:
                # Process images to find manufacturer matches
                image_results = await process_product_images(
                    images, mpn, manufacturer, request_id
                )

                # Add image URL to response
                response["image_url"] = image_results.get("image_url")
                if "manufacturer_match" in image_results and image_results["manufacturer_match"]:
                    logger.info(f"{debug_prefix}Found manufacturer-specific image")

        # Process attribute extraction results
        if "attribute_extraction" in results and results["attribute_extraction"]:
            response_data = results["attribute_extraction"]

            # Store token information in the response
            response["token_data"]["input_tokens"] = response_data["tokens"]["input"]
            response["token_data"]["output_tokens"] = response_data["tokens"]["output"]
            response["token_data"]["total_tokens"] = response_data["tokens"]["input"] + response_data["tokens"]["output"]
            response["token_data"]["cost_inr"] = response_data["costs"]["inr"]["total"]

            # Update global token stats if enabled
            if settings.ENABLE_TOKEN_TRACKING:
                token_stats.update(
                    response_data["tokens"]["input"],
                    response_data["tokens"]["output"],
                    response_data["costs"]["inr"]["total"]
                )

            # Store the raw response from Gemini
            response["raw_gemini_response"] = response_data["text"]

            # Extract JSON data from response
            attribute_data = await extract_json_from_response(response_data, request_id)

            if attribute_data:
                # Filter attributes to only include requested ones if provided
                if final_attributes_to_extract:
                    filtered_attributes = {}
                    for key, value in attribute_data.items():
                        if key in final_attributes_to_extract:
                            filtered_attributes[key] = value
                    response["attributes"] = filtered_attributes
                    logger.info(f"{debug_prefix}Filtered attributes from {len(attribute_data)} to {len(filtered_attributes)} based on requested fields")
                else:
                    response["attributes"] = attribute_data

                # Set confidence based on number of attributes extracted
                expected_attrs = len(final_attributes_to_extract)
                actual_attrs = len(response["attributes"])

                if expected_attrs > 0:
                    ratio = actual_attrs / expected_attrs
                    if ratio > 0.8:
                        response["confidence"] = "HIGH"
                    elif ratio > 0.5:
                        response["confidence"] = "MEDIUM"
                    else:
                        response["confidence"] = "LOW"
                elif actual_attrs > 5:
                    response["confidence"] = "MEDIUM"

    # Calculate processing time
    processing_time = time.time() - start_time
    response["processing_time_seconds"] = round(processing_time, 2)

    logger.info(f"{debug_prefix}Completed enrichment in {processing_time:.2f} seconds")
    return response

# -------------------- Batch Processing --------------------

async def process_bulk_file(
    df: pd.DataFrame, 
    include_images: bool, 
    batch_size: int, 
    task_id: str
) -> str:
    """
    Process a dataframe of products in batches
    
    Args:
        df: DataFrame containing product data
        include_images: Whether to include images in the results
        batch_size: Number of products to process in each batch
        task_id: Task ID for logging
        
    Returns:
        str: Path to the output file
    """
    logger.info(f"[{task_id}] Starting background processing of {len(df)} rows")

    # Create output dataframe
    output_df = df.copy()

    # Add columns for results
    if include_images and 'image_url' not in output_df.columns:
        output_df['image_url'] = ""

    # Add attribute columns
    for col in ['attributes_json', 'confidence', 'processing_time', 'raw_gemini_response', 'requested_attributes', 
                'input_tokens', 'output_tokens', 'total_tokens', 'cost_inr']:
        if col not in output_df.columns:
            output_df[col] = ""

    # Reset token stats for this batch
    if settings.ENABLE_TOKEN_TRACKING:
        token_stats.reset()

    # Process in batches
    total_rows = len(df)
    for batch_start in range(0, total_rows, batch_size):
        batch_end = min(batch_start + batch_size, total_rows)
        logger.info(f"[{task_id}] Processing batch {batch_start}-{batch_end}")

        # Create tasks for this batch
        batch_tasks = []
        row_indices = []

        for idx in range(batch_start, batch_end):
            row = df.iloc[idx]

            # Extract data from row
            mpn = str(row['mfg_part_number'])
            manufacturer = str(row['manufacturer_name']) if 'manufacturer_name' in row and pd.notna(row['manufacturer_name']) else None

            # For category/subcategory, check if already assigned or in columns
            category = row.get('category_gen', None)
            subcategory = row.get('sub_category_gen', None)

            # Set up attribute extraction based on available columns
            attributes_to_extract = []
            # Check if there's a column with attributes to extract
            if 'attributes_to_extract' in row and pd.notna(row['attributes_to_extract']):
                attributes_str = str(row['attributes_to_extract'])
                attributes_to_extract = [attr.strip() for attr in attributes_str.split(',')]

            # Create the enrichment task
            task = enrich_product_data(
                mpn=mpn,
                manufacturer=manufacturer,
                category=category,
                subcategory=subcategory,
                attributes_to_extract=attributes_to_extract,
                include_images=include_images,
                request_id=f"{task_id}-row{idx}"
            )

            batch_tasks.append(task)
            row_indices.append(idx)

        # Execute all tasks in this batch concurrently using asyncio.gather
        try:
            # Use gather to run all tasks concurrently and wait for all to complete
            results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Process the results
            for idx, result in zip(row_indices, results):
                # Skip if an exception was returned
                if isinstance(result, Exception):
                    logger.error(f"[{task_id}] Error processing row {idx}: {str(result)}")
                    output_df.at[idx, 'error'] = str(result)
                    continue

                # Store results in output dataframe
                if result.get("image_url"):
                    output_df.at[idx, 'image_url'] = result["image_url"]

                # Store the raw Gemini response if available
                if "raw_gemini_response" in result:
                    output_df.at[idx, 'raw_gemini_response'] = result["raw_gemini_response"]

                # Store the requested attributes
                if "requested_attributes" in result and result["requested_attributes"]:
                    output_df.at[idx, 'requested_attributes'] = ','.join(result["requested_attributes"])

                # Store token information
                if "token_data" in result:
                    output_df.at[idx, 'input_tokens'] = result["token_data"]["input_tokens"]
                    output_df.at[idx, 'output_tokens'] = result["token_data"]["output_tokens"]
                    output_df.at[idx, 'total_tokens'] = result["token_data"]["total_tokens"]
                    output_df.at[idx, 'cost_inr'] = result["token_data"]["cost_inr"]

                # Store attributes as JSON
                output_df.at[idx, 'attributes_json'] = json.dumps(result.get("attributes", {}))
                output_df.at[idx, 'confidence'] = result.get("confidence", "LOW")
                output_df.at[idx, 'processing_time'] = result.get("processing_time_seconds", 0)

                # Store individual attributes if they exist
                requested_attrs = result.get("requested_attributes", [])
                for key, value in result.get("attributes", {}).items():
                    # Only process attributes that were in the requested list
                    if not requested_attrs or key in requested_attrs:
                        # Create column if it doesn't exist
                        col_name = f'attr_{key.lower().replace(" ", "_")}'
                        if col_name not in output_df.columns:
                            output_df[col_name] = ""

                        # Store the value
                        output_df.at[idx, col_name] = value

        except Exception as e:
            logger.error(f"[{task_id}] Error processing batch: {str(e)}")

    # Get token stats for summary
    if settings.ENABLE_TOKEN_TRACKING:
        stats = token_stats.get_stats()
        total_input = stats['total_input_tokens']
        total_output = stats['total_output_tokens']
        total_cost = stats['total_cost_inr']
    else:
        total_input = 0
        total_output = 0
        total_cost = 0

    # Add summary row if there is at least one row
    if len(output_df) > 0:
        # Add a summary column to the dataframe
        output_df['is_summary'] = False

        # Create a summary row
        summary_data = {
            'mfg_part_number': "SUMMARY",
            'input_tokens': total_input,
            'output_tokens': total_output,
            'total_tokens': total_input + total_output,
            'cost_inr': total_cost,
            'is_summary': True
        }

        # Append summary row to the dataframe
        summary_df = pd.DataFrame([summary_data])
        output_df = pd.concat([output_df, summary_df], ignore_index=True)

    # Save results to file
    try:
        output_path = get_output_path()
        output_df.to_excel(output_path, index=False)
        logger.info(f"[{task_id}] Saved results to {output_path}")

        # Log final summary
        logger.info(f"[{task_id}] Processing complete. Summary:")
        logger.info(f"[{task_id}] Total rows processed: {total_rows}")
        logger.info(f"[{task_id}] Total input tokens: {total_input}")
        logger.info(f"[{task_id}] Total output tokens: {total_output}")
        logger.info(f"[{task_id}] Total tokens: {total_input + total_output}")
        logger.info(f"[{task_id}] Total cost (INR): ₹{total_cost:.6f}")

        return output_path

    except Exception as e:
        logger.error(f"[{task_id}] Error saving results: {str(e)}")
        return ""