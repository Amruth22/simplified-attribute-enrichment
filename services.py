"""
External services integration for the Simplified Attribute Enrichment service
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional

from google import genai
from google.genai import types
from googleapiclient.discovery import build

from config import settings
from utils import get_debug_prefix, count_tokens, calculate_token_costs, is_valid_url

# Configure logging
logger = logging.getLogger("attribute_enricher.services")

# -------------------- Gemini Service --------------------

async def generate_gemini_response(prompt: str, request_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Use Gemini to generate a response based on the given prompt

    Args:
        prompt: The prompt text to send to Gemini
        request_id: Request ID for logging

    Returns:
        dict: Contains response text and token information
    """
    debug_prefix = get_debug_prefix(request_id)

    try:
        # Count tokens in the input prompt
        input_tokens = count_tokens(prompt)
        logger.info(f"{debug_prefix}Input prompt has {input_tokens} tokens")

        # Check if API key is configured
        if not settings.GOOGLE_API_KEY:
            logger.error(f"{debug_prefix}GOOGLE_API_KEY is not set. Cannot call Gemini API.")
            # Return a mock response for testing
            return {
                "text": '{"error": "API key not configured"}',
                "tokens": {
                    "input": input_tokens,
                    "output": 0,
                    "total": input_tokens
                },
                "costs": {
                    "inr": {
                        "input": 0,
                        "output": 0,
                        "total": 0
                    }
                }
            }

        # Initialize Gemini client
        logger.info(f"{debug_prefix}Initializing Gemini client with project: {settings.GEMINI_PROJECT_ID}")
        try:
            client = genai.Client(
                vertexai=True,
                project=settings.GEMINI_PROJECT_ID,
                location=settings.GEMINI_LOCATION,
            )
            logger.info(f"{debug_prefix}Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"{debug_prefix}Error initializing Gemini client: {str(e)}")
            raise

        # Configure Google Search tool
        google_search_tool = types.Tool(google_search=types.GoogleSearch())

        # Configure generation parameters
        generate_content_config = types.GenerateContentConfig(
            temperature=0.0,
            top_p=0.9,
            max_output_tokens=1000,
            response_modalities=["TEXT"],
            response_mime_type='application/json',
            tools=[google_search_tool],
            safety_settings=[
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
            ],
        )

        # Prepare content for Gemini
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
        ]

        # Get response from Gemini using async API
        logger.info(f"{debug_prefix}Sending prompt to Gemini model: {settings.GEMINI_MODEL}")
        try:
            response = await client.aio.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=contents,
                config=generate_content_config,
            )
            logger.info(f"{debug_prefix}Received response from Gemini API")
        except Exception as e:
            logger.error(f"{debug_prefix}Error calling Gemini API: {str(e)}")
            # For debugging, return a mock response
            return {
                "text": f'{{"error": "API call failed: {str(e)}"}}',
                "tokens": {
                    "input": input_tokens,
                    "output": 0,
                    "total": input_tokens
                },
                "costs": {
                    "inr": {
                        "input": 0,
                        "output": 0,
                        "total": 0
                    }
                }
            }

        result_text = response.text
        logger.info(f"{debug_prefix}Received response from Gemini ({len(result_text)} chars)")

        # Count tokens in the output response
        output_tokens = count_tokens(result_text)
        logger.info(f"{debug_prefix}Output response has {output_tokens} tokens")

        # Calculate costs
        costs = calculate_token_costs(input_tokens, output_tokens)
        logger.info(f"{debug_prefix}API call cost: ₹{costs['inr']['total']:.6f}")

        return {
            "text": result_text,
            "tokens": {
                "input": input_tokens,
                "output": output_tokens,
                "total": input_tokens + output_tokens
            },
            "costs": costs
        }

    except Exception as e:
        logger.error(f"{debug_prefix}Error in Gemini API call: {str(e)}")
        # Return a mock response for testing
        return {
            "text": f'{{"error": "Exception occurred: {str(e)}"}}',
            "tokens": {
                "input": input_tokens if 'input_tokens' in locals() else 0,
                "output": 0,
                "total": input_tokens if 'input_tokens' in locals() else 0
            },
            "costs": {
                "inr": {
                    "input": 0,
                    "output": 0,
                    "total": 0
                }
            }
        }

# -------------------- Google Search Service --------------------

async def search_part_images_async(
    part_number: str, 
    supplier: Optional[str] = None, 
    request_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for images of a specific product using Google Custom Search API

    Args:
        part_number: The product part number to search for
        supplier: Optional supplier/manufacturer name to refine search
        request_id: Request ID for logging

    Returns:
        list: List of image data dictionaries
    """
    debug_prefix = get_debug_prefix(request_id)

    try:
        logger.info(f"{debug_prefix}Searching for images of part {part_number}")

        # Google Custom Search API configuration
        api_key = settings.GOOGLE_API_KEY
        cse_id = settings.GOOGLE_CSE_ID
        
        # Check if API key and CSE ID are configured
        if not api_key or not cse_id:
            logger.warning(f"{debug_prefix}Google API key or CSE ID not configured")
            return []
            
        num_results = 10

        # Build the service object
        service = build("customsearch", "v1", developerKey=api_key)

        # Construct the search query
        query = f"{part_number} product"
        if supplier:
            query += f" {supplier}"

        # Create a thread pool for the API call
        loop = asyncio.get_event_loop()

        # Execute the search request in a thread to not block the event loop
        result = await loop.run_in_executor(
            None, 
            lambda: service.cse().list(
                q=query,
                cx=cse_id,
                searchType='image',
                num=num_results,
                imgType='photo',
                fileType='jpg|png',
                safe='off'
            ).execute()
        )

        # Check if there are any results
        if 'items' not in result:
            logger.info(f"{debug_prefix}No image results found for part number: {part_number}")
            return []

        # Process image results
        images = []
        for item in result['items']:
            # Skip invalid image URLs
            if 'link' not in item or not item['link'] or item['link'].startswith('x-raw-image:'):
                continue

            # Ensure URL is a standard web URL (http or https)
            image_url = item['link']
            if not is_valid_url(image_url):
                continue

            # Create the image data dictionary
            image_data = {
                'title': item.get('title', 'Product Image'),
                'url': image_url,
                'source': item.get('image', {}).get('contextLink', ''),
                'source_url': item.get('image', {}).get('contextLink', ''),
                'height': item.get('image', {}).get('height', 0),
                'width': item.get('image', {}).get('width', 0),
                'thumbnail': item.get('image', {}).get('thumbnailLink', '')
            }

            # Validate URLs in the data
            for key in ['url', 'source', 'source_url', 'thumbnail']:
                if key in image_data and image_data[key]:
                    url_value = image_data[key]
                    if not is_valid_url(url_value):
                        image_data[key] = ''

            images.append(image_data)

        logger.info(f"{debug_prefix}Found {len(images)} valid images for part {part_number}")
        return images

    except Exception as e:
        logger.error(f"{debug_prefix}Error in Google Custom Search: {str(e)}")
        return []

# -------------------- Image Processing --------------------

async def process_product_images(
    images: List[Dict[str, Any]], 
    mpn: str, 
    manufacturer: Optional[str] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process product images to find the best match
    
    Args:
        images: List of image data dictionaries
        mpn: Manufacturer part number
        manufacturer: Optional manufacturer name
        request_id: Request ID for logging
        
    Returns:
        dict: Best image match information
    """
    debug_prefix = get_debug_prefix(request_id)
    logger.info(f"{debug_prefix}Processing {len(images)} images for part {mpn}")
    
    # Default result
    result = {
        "image_url": None,
        "thumbnail_url": None,
        "source_url": None,
        "manufacturer_match": False,
        "confidence": "LOW"
    }
    
    if not images:
        return result
    
    # First, try to find an image from the manufacturer's website
    if manufacturer:
        manufacturer_lower = manufacturer.lower()
        for image in images:
            source_url = image.get('source_url', '').lower()
            if manufacturer_lower in source_url:
                result["image_url"] = image.get('url')
                result["thumbnail_url"] = image.get('thumbnail')
                result["source_url"] = image.get('source_url')
                result["manufacturer_match"] = True
                result["confidence"] = "HIGH"
                logger.info(f"{debug_prefix}Found manufacturer-specific image for {mpn}")
                return result
    
    # If no manufacturer match, use the first valid image
    for image in images:
        image_url = image.get('url')
        if is_valid_url(image_url):
            result["image_url"] = image_url
            result["thumbnail_url"] = image.get('thumbnail')
            result["source_url"] = image.get('source_url')
            result["confidence"] = "MEDIUM"
            logger.info(f"{debug_prefix}Using first valid image for {mpn}")
            return result
    
    # If we get here, no valid images were found
    logger.info(f"{debug_prefix}No valid images found for {mpn}")
    return result