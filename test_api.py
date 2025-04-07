"""
Test script for the Simplified Attribute Enrichment API
"""
import requests
import json
import sys
import os

# API base URL
BASE_URL = "http://localhost:8080"

def test_health():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print("-" * 50)

def test_single_enrichment():
    """Test the single product enrichment endpoint"""
    data = {
        "mpn": "ABC123",
        "manufacturer": "Example Corp",
        "category": "Electrical",
        "subcategory": "Switches",
        "attributes_to_extract": ["Material", "Width", "Height", "Voltage"],
        "include_images": True
    }
    
    print(f"Sending request to enrich product: {data['mpn']}")
    response = requests.post(f"{BASE_URL}/api/v1/enrich", json=data)
    
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("Extracted attributes:")
        print(json.dumps(result["attributes"], indent=2))
        print(f"Image URL: {result['image_url']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Processing time: {result['processing_time_seconds']} seconds")
        print(f"Token usage: {result['token_data']['total_tokens']} tokens")
        print(f"Cost: ₹{result['token_data']['cost_inr']}")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)

def test_bulk_enrichment():
    """Test the bulk enrichment endpoint"""
    if not os.path.exists("example_input.csv"):
        print("Error: example_input.csv not found")
        return
    
    with open("example_input.csv", "rb") as file:
        files = {"file": file}
        data = {"include_images": "true", "batch_size": "2"}
        
        print("Sending bulk enrichment request")
        response = requests.post(
            f"{BASE_URL}/api/v1/bulk-enrich",
            files=files,
            data=data
        )
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Task ID: {result['task_id']}")
            print(f"Status: {result['status']}")
            print(f"Message: {result['message']}")
            print(f"Total rows: {result['total_rows']}")
            print(f"Estimated time: {result['estimated_time_seconds']} seconds")
        else:
            print(f"Error: {response.text}")
    print("-" * 50)

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "health":
            test_health()
        elif sys.argv[1] == "single":
            test_single_enrichment()
        elif sys.argv[1] == "bulk":
            test_bulk_enrichment()
        else:
            print(f"Unknown test: {sys.argv[1]}")
    else:
        # Run all tests
        print("Running all tests...")
        test_health()
        test_single_enrichment()
        test_bulk_enrichment()