"""
Run script for the Simplified Attribute Enrichment API
"""
import os
import sys
import uvicorn
from config import settings

def check_environment():
    """Check if the environment is properly configured"""
    # Check for required directories
    for directory in ['data', 'output']:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")
    
    # Check for API keys
    if not settings.GOOGLE_API_KEY:
        print("WARNING: GOOGLE_API_KEY is not set. Image search will not work.")
    
    if not settings.GOOGLE_CSE_ID:
        print("WARNING: GOOGLE_CSE_ID is not set. Image search will not work.")
    
    # Check for taxonomy file
    if not os.path.exists(settings.TAXONOMY_PATH):
        print(f"WARNING: Taxonomy file not found at {settings.TAXONOMY_PATH}")
        print("The application will still work, but attribute extraction may be limited.")

def run_server():
    """Run the FastAPI server"""
    print(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)

if __name__ == "__main__":
    print("Simplified Attribute Enrichment API")
    print("=" * 40)
    
    # Check environment
    check_environment()
    
    # Run server
    run_server()