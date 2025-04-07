# Simplified Attribute Enrichment

A streamlined FastAPI application for enriching product data with attribute information and images using Google's Gemini AI.

## Overview

This service extracts detailed product attributes and images for manufacturing parts using AI. It's designed to be simple, efficient, and easy to maintain with a minimalist file structure.

## Features

- **Single Product Enrichment**: Extract detailed attributes for a single product
- **Bulk Enrichment**: Process multiple products from a CSV or Excel file
- **Image Search**: Find relevant product images using Google Custom Search
- **Category-Specific Templates**: Specialized prompts for different product categories
- **Token Usage Tracking**: Monitor API usage and costs

## Project Structure

The project follows a simplified structure for better readability and reduced complexity:

```
simplified-attribute-enrichment/
├── main.py                # FastAPI app + API routes
├── config.py              # Configuration settings
├── models.py              # Data models
├── enrichment.py          # Core enrichment logic
├── services.py            # External services integration
├── templates.py           # Prompt templates
└── utils.py               # Utility functions
```

## API Endpoints

### Health Check
```
GET /health
```

### Single Product Enrichment
```
POST /api/v1/enrich
```

Request body:
```json
{
  "mpn": "ABC123",
  "manufacturer": "Example Corp",
  "category": "Electrical",
  "subcategory": "Switches",
  "attributes_to_extract": ["Material", "Width", "Height", "Voltage"],
  "include_images": true
}
```

### Bulk Enrichment
```
POST /api/v1/bulk-enrich
```

Form data:
- `file`: CSV or Excel file with product data
- `include_images`: Whether to include images (boolean)
- `batch_size`: Number of products to process in each batch (integer)

## Setup and Installation

1. Clone the repository
   ```
   git clone https://github.com/Amruth22/simplified-attribute-enrichment.git
   cd simplified-attribute-enrichment
   ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables
   ```
   # Create a .env file with the following variables
   GOOGLE_API_KEY=your_api_key
   GOOGLE_CSE_ID=your_cse_id
   ```

4. Run the application
   ```
   python main.py
   ```
   
   Or with uvicorn directly:
   ```
   uvicorn main:app --reload
   ```

## Configuration

Edit `config.py` to customize settings:

- API host and port
- Google API credentials
- Gemini API settings
- Processing limits
- Token cost calculations

## Usage Examples

### Python Client

```python
import requests
import json

# Single product enrichment
response = requests.post(
    "http://localhost:8080/api/v1/enrich",
    json={
        "mpn": "ABC123",
        "manufacturer": "Example Corp",
        "category": "Electrical",
        "attributes_to_extract": ["Material", "Width", "Height"]
    }
)
result = response.json()
print(json.dumps(result, indent=2))

# Bulk enrichment
with open("products.csv", "rb") as file:
    response = requests.post(
        "http://localhost:8080/api/v1/bulk-enrich",
        files={"file": file},
        data={"include_images": "true", "batch_size": "50"}
    )
result = response.json()
print(json.dumps(result, indent=2))
```

## Input File Format

For bulk processing, your CSV or Excel file should have at least these columns:

- `mfg_part_number` (required): The manufacturer part number
- `manufacturer_name` (optional): The manufacturer name
- `category_gen` (optional): Product category
- `sub_category_gen` (optional): Product subcategory
- `attributes_to_extract` (optional): Comma-separated list of attributes to extract

Example:
```
mfg_part_number,manufacturer_name,category_gen,sub_category_gen,attributes_to_extract
ABC123,Example Corp,Electrical,Switches,"Material,Width,Height,Voltage"
DEF456,Another Mfg,HVAC,Filters,"Material,Dimensions,MERV Rating"
```

## Output Format

The service generates an Excel file with the original data plus:

- Extracted attributes (both as JSON and individual columns)
- Image URLs (if requested)
- Processing metadata (confidence, token usage, costs)

## License

MIT