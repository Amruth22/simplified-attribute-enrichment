# Simplified Attribute Enrichment

A streamlined FastAPI application for enriching product data with attribute information and images using Google's Gemini AI.

<div align="center">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/framework-FastAPI-green" alt="FastAPI">
  <img src="https://img.shields.io/badge/AI-Gemini%202.0-orange" alt="Gemini 2.0">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="License: MIT">
</div>

## 📋 Overview

This service extracts detailed product attributes and images for manufacturing parts using AI. It's designed to be simple, efficient, and easy to maintain with a minimalist file structure. The application uses Google's Gemini AI to analyze product information and extract structured data.

### 🌟 Key Benefits

- **Automated Data Extraction**: Save hours of manual research and data entry
- **Consistent Format**: Get structured data in a standardized format
- **Scalable Processing**: Handle individual products or bulk datasets
- **Cost Tracking**: Monitor token usage and associated costs
- **Simple Codebase**: Easy to understand, maintain, and extend

## ✨ Features

- **Single Product Enrichment**: Extract detailed attributes for a single product
- **Bulk Enrichment**: Process multiple products from a CSV or Excel file
- **Image Search**: Find relevant product images using Google Custom Search
- **Category-Specific Templates**: Specialized prompts for different product categories:
  - Electrical
  - HVAC
  - Plumbing
  - Refrigeration
- **Token Usage Tracking**: Monitor API usage and costs
- **Background Processing**: Handle large datasets without blocking
- **Flexible Output**: Get results as JSON or Excel files

## 🏗️ Project Structure

The project follows a simplified structure for better readability and reduced complexity:

```
simplified-attribute-enrichment/
├── main.py                # FastAPI app + API routes
├── config.py              # Configuration settings
├── models.py              # Data models
├── enrichment.py          # Core enrichment logic
├── services.py            # External services integration
├── templates.py           # Prompt templates
├── utils.py               # Utility functions
├── run.py                 # Script to run the application
├── test_api.py            # Script to test the API
├── requirements.txt       # Dependencies
├── .env                   # Environment variables (update with your keys)
├── example_input.csv      # Example input file
├── data/                  # Directory for taxonomy data
└── output/                # Directory for output files
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Google API Key for Custom Search
- Google Custom Search Engine ID
- Access to Google's Gemini API

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/Amruth22/simplified-attribute-enrichment.git
   cd simplified-attribute-enrichment
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Update the `.env` file with your API keys
   ```bash
   # Edit the .env file
   GOOGLE_API_KEY=your_google_api_key_here
   GOOGLE_CSE_ID=your_google_cse_id_here
   ```

4. Run the application
   ```bash
   python run.py
   ```

5. Access the API documentation at http://localhost:8080/docs

### Testing the API

Use the included test script to verify the API is working:

```bash
# Test all endpoints
python test_api.py

# Test specific endpoints
python test_api.py health
python test_api.py single
python test_api.py bulk
```

## 🔌 API Endpoints

### Health Check
```
GET /health
```
Returns the current status of the API.

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

Response:
```json
{
  "mpn": "ABC123",
  "manufacturer": "Example Corp",
  "category": "Electrical",
  "subcategory": "Switches",
  "image_url": "https://example.com/image.jpg",
  "attributes": {
    "Material": "Plastic",
    "Width": "2.5 inches",
    "Height": "4 inches",
    "Voltage": "120V"
  },
  "processing_time_seconds": 3.45,
  "confidence": "HIGH",
  "requested_attributes": ["Material", "Width", "Height", "Voltage"],
  "token_data": {
    "input_tokens": 250,
    "output_tokens": 150,
    "total_tokens": 400,
    "cost_inr": 0.0034
  }
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

Response:
```json
{
  "status": "processing",
  "task_id": "task-1712345678",
  "message": "Processing 4 rows in the background",
  "total_rows": 4,
  "estimated_time_seconds": 8
}
```

## ⚙️ Configuration

Edit `config.py` or the `.env` file to customize settings:

### API Settings
- `HOST`: API host address (default: 127.0.0.1)
- `PORT`: API port (default: 8080)

### Google API Settings
- `GOOGLE_API_KEY`: Your Google API key
- `GOOGLE_CSE_ID`: Your Custom Search Engine ID

### Gemini API Settings
- `GEMINI_PROJECT_ID`: Google Cloud project ID
- `GEMINI_LOCATION`: Google Cloud region
- `GEMINI_MODEL`: Gemini model to use

### Processing Settings
- `MAX_BATCH_SIZE`: Maximum batch size for bulk processing
- `MAX_ROWS_TO_PROCESS`: Maximum rows to process in a single request
- `ENABLE_TOKEN_TRACKING`: Whether to track token usage

### Token Cost Settings
- `USD_TO_INR`: USD to INR conversion rate
- `INPUT_TOKEN_COST_PER_MILLION`: Cost per million input tokens
- `OUTPUT_TOKEN_COST_PER_MILLION`: Cost per million output tokens

## 📊 Input & Output

### Input File Format

For bulk processing, your CSV or Excel file should have at least these columns:

- `mfg_part_number` (required): The manufacturer part number
- `manufacturer_name` (optional): The manufacturer name
- `category_gen` (optional): Product category
- `sub_category_gen` (optional): Product subcategory
- `attributes_to_extract` (optional): Comma-separated list of attributes to extract

Example CSV:
```csv
mfg_part_number,manufacturer_name,category_gen,sub_category_gen,attributes_to_extract
ABC123,Example Corp,Electrical,Switches,"Material,Width,Height,Voltage"
DEF456,Another Mfg,HVAC,Filters,"Material,Dimensions,MERV Rating"
GHI789,Cool Tech,Refrigeration,Compressors,"Material,Capacity,Refrigerant Type"
```

### Output Format

The service generates an Excel file in the `output` directory with:

- All original columns from the input file
- `image_url`: URL to the product image (if requested)
- `attributes_json`: JSON string with all extracted attributes
- `confidence`: Confidence level (LOW, MEDIUM, HIGH)
- `processing_time`: Time taken to process in seconds
- `input_tokens`, `output_tokens`, `total_tokens`: Token usage
- `cost_inr`: Cost in Indian Rupees
- Individual attribute columns (e.g., `attr_material`, `attr_width`)
- A summary row with total token usage and costs

## 💻 Usage Examples

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
with open("example_input.csv", "rb") as file:
    response = requests.post(
        "http://localhost:8080/api/v1/bulk-enrich",
        files={"file": file},
        data={"include_images": "true", "batch_size": "2"}
    )
result = response.json()
print(json.dumps(result, indent=2))
```

### cURL

```bash
# Single product enrichment
curl -X POST "http://localhost:8080/api/v1/enrich" \
  -H "Content-Type: application/json" \
  -d '{"mpn":"ABC123","manufacturer":"Example Corp","category":"Electrical","attributes_to_extract":["Material","Width","Height"]}'

# Bulk enrichment (using form data)
curl -X POST "http://localhost:8080/api/v1/bulk-enrich" \
  -F "file=@example_input.csv" \
  -F "include_images=true" \
  -F "batch_size=2"
```

## 🧩 How It Works

1. **Template Selection**: The system selects a category-specific prompt template
2. **Prompt Generation**: Creates a detailed prompt with the product information
3. **Gemini API**: Sends the prompt to Google's Gemini AI
4. **Image Search**: Concurrently searches for product images (if requested)
5. **Response Processing**: Extracts structured data from the AI response
6. **Result Formatting**: Returns the data in the requested format

## 🔍 Supported Product Categories

The system has specialized templates for these categories:

1. **Electrical**: Switches, breakers, connectors, etc.
2. **HVAC**: Heating, ventilation, and air conditioning components
3. **Plumbing**: Valves, fittings, pipes, etc.
4. **Refrigeration**: Compressors, condensers, refrigerants, etc.

For other categories, a generic template is used.

## 🛠️ Extending the System

### Adding New Templates

To add a new product category template:

1. Add a new template class in `templates.py`
2. Update the `get_template()` function to return your new template

### Customizing Prompts

Each template has a `generate_prompt()` method that you can customize to improve results for specific product types.

## 📝 License

MIT

## 🙏 Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
- [Google Gemini AI](https://ai.google.dev/) - The AI model powering attribute extraction
- [Google Custom Search](https://developers.google.com/custom-search) - For image search functionality