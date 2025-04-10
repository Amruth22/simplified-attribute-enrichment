"""
Utility functions for the Simplified Attribute Enrichment service
"""
import json
import logging
import re
import time
from typing import Dict, Any, Optional, Tuple

from config import settings

# -------------------- Logging Utilities --------------------

def get_debug_prefix(request_id: Optional[str] = None) -> str:
    """
    Get a debug prefix for logging
    
    Args:
        request_id: Optional request ID
        
    Returns:
        str: Debug prefix for logging
    """
    if request_id:
        return f"[{request_id}] "
    return ""

def setup_logging() -> None:
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# -------------------- JSON Utilities --------------------

async def extract_json_from_response(response_data: Dict[str, Any], request_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract JSON data from a Gemini response
    
    Args:
        response_data: Response data from Gemini
        request_id: Optional request ID for logging
        
    Returns:
        dict: Extracted JSON data
    """
    debug_prefix = get_debug_prefix(request_id)
    logger = logging.getLogger("attribute_enricher.utils.json")
    
    try:
        # Get the text from the response
        text = response_data.get("text", "")
        
        if not text:
            logger.warning(f"{debug_prefix}Empty response text")
            return {}
            
        logger.info(f"{debug_prefix}Attempting to extract JSON from response ({len(text)} chars)")
        
        # Try to parse the entire response as JSON first
        try:
            logger.info(f"{debug_prefix}Trying to parse entire response as JSON")
            json_data = json.loads(text)
            logger.info(f"{debug_prefix}Successfully parsed entire response as JSON")
            return json_data
        except json.JSONDecodeError as e:
            logger.info(f"{debug_prefix}Response is not a valid JSON object: {str(e)}")
        
        # Try to extract JSON using regex pattern
        logger.info(f"{debug_prefix}Trying to extract JSON using regex")
        json_pattern = r'({[\s\S]*})'
        match = re.search(json_pattern, text)
        
        if match:
            json_str = match.group(1)
            logger.info(f"{debug_prefix}Found potential JSON string ({len(json_str)} chars)")
            try:
                json_data = json.loads(json_str)
                logger.info(f"{debug_prefix}Successfully parsed extracted JSON")
                return json_data
            except json.JSONDecodeError as e:
                logger.warning(f"{debug_prefix}Extracted text is not valid JSON: {str(e)}")
                
                # Try to fix common JSON issues
                logger.info(f"{debug_prefix}Attempting to fix JSON formatting issues")
                fixed_json_str = fix_json_formatting(json_str)
                try:
                    json_data = json.loads(fixed_json_str)
                    logger.info(f"{debug_prefix}Successfully parsed fixed JSON")
                    return json_data
                except json.JSONDecodeError as e:
                    logger.warning(f"{debug_prefix}Fixed JSON is still invalid: {str(e)}")
        else:
            logger.warning(f"{debug_prefix}No JSON-like structure found in response")
        
        # If we get here, we couldn't extract valid JSON
        # Log a snippet of the response for debugging
        text_snippet = text[:200] + "..." if len(text) > 200 else text
        logger.warning(f"{debug_prefix}Could not extract valid JSON from response. Text snippet: {text_snippet}")
        return {}
        
    except Exception as e:
        logger.error(f"{debug_prefix}Error extracting JSON: {str(e)}")
        return {}

def fix_json_formatting(json_str: str) -> str:
    """
    Attempt to fix common JSON formatting issues
    
    Args:
        json_str: JSON string to fix
        
    Returns:
        str: Fixed JSON string
    """
    # Replace single quotes with double quotes
    fixed = json_str.replace("'", '"')
    
    # Fix trailing commas in objects
    fixed = re.sub(r',\s*}', '}', fixed)
    
    # Fix trailing commas in arrays
    fixed = re.sub(r',\s*]', ']', fixed)
    
    # Ensure property names are double-quoted
    fixed = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', fixed)
    
    return fixed

# -------------------- Token Utilities --------------------

def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a text string
    
    This is a simplified implementation. In a production environment,
    you would use a proper tokenizer like tiktoken.
    
    Args:
        text: Text to count tokens for
        
    Returns:
        int: Estimated token count
    """
    # Simple approximation: 1 token ≈ 4 characters
    return len(text) // 4

def calculate_token_costs(input_tokens: int, output_tokens: int) -> Dict[str, Any]:
    """
    Calculate the cost of tokens
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        
    Returns:
        dict: Cost information
    """
    # Calculate costs in USD
    input_cost_usd = (input_tokens / 1_000_000) * settings.INPUT_TOKEN_COST_PER_MILLION
    output_cost_usd = (output_tokens / 1_000_000) * settings.OUTPUT_TOKEN_COST_PER_MILLION
    total_cost_usd = input_cost_usd + output_cost_usd
    
    # Convert to INR
    input_cost_inr = input_cost_usd * settings.USD_TO_INR
    output_cost_inr = output_cost_usd * settings.USD_TO_INR
    total_cost_inr = total_cost_usd * settings.USD_TO_INR
    
    return {
        "usd": {
            "input": input_cost_usd,
            "output": output_cost_usd,
            "total": total_cost_usd
        },
        "inr": {
            "input": input_cost_inr,
            "output": output_cost_inr,
            "total": total_cost_inr
        }
    }

# -------------------- Time Utilities --------------------

def get_timestamp() -> str:
    """Get a formatted timestamp string"""
    return time.strftime("%Y%m%d_%H%M%S")

def get_task_id() -> str:
    """Generate a unique task ID"""
    return f"task-{int(time.time())}"

# -------------------- URL Utilities --------------------

def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid
    
    Args:
        url: URL to check
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not url:
        return False
    
    # Simple validation - should start with http:// or https://
    return url.startswith("http://") or url.startswith("https://")

# -------------------- File Utilities --------------------

def ensure_output_directory() -> None:
    """Ensure the output directory exists"""
    import os
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

def get_output_path(prefix: str = "enriched_data") -> str:
    """
    Get a path for an output file
    
    Args:
        prefix: Prefix for the filename
        
    Returns:
        str: Output file path
    """
    ensure_output_directory()
    timestamp = get_timestamp()
    return f"{settings.OUTPUT_DIR}/{prefix}_{timestamp}.xlsx"