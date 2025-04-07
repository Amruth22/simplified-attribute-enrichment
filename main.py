"""
Simplified Attribute Enrichment - Main Application Entry Point
"""
import time
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import pandas as pd
import os

# Import configuration
from config import settings

# Import models
from models import EnrichmentRequest, EnrichmentResponse, BulkEnrichmentResponse

# Import core functionality
from enrichment import enrich_product_data, process_bulk_file

# Import utilities
from utils import setup_logging, get_task_id

# Configure logging
setup_logging()
logger = logging.getLogger("attribute_enricher")

# Create FastAPI app
app = FastAPI(
    title="Simplified Attribute Enrichment API",
    description="API for enriching product data with attribute information and images",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- API Routes --------------------

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

@app.post("/api/v1/enrich", response_model=EnrichmentResponse)
async def enrich_product(request: EnrichmentRequest):
    """
    Enrich a single product with attribute data and optionally images
    
    Args:
        request: Product enrichment request
        
    Returns:
        EnrichmentResponse: Enriched product data
    """
    request_id = f"single-{int(time.time())}"
    
    try:
        # Call the core enrichment function
        result = await enrich_product_data(
            mpn=request.mpn,
            manufacturer=request.manufacturer,
            category=request.category,
            subcategory=request.subcategory,
            attributes_to_extract=request.attributes_to_extract,
            include_images=request.include_images,
            request_id=request_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"[{request_id}] Error enriching product: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error enriching product: {str(e)}")

@app.post("/api/v1/bulk-enrich", response_model=BulkEnrichmentResponse)
async def bulk_enrich(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    include_images: bool = Form(False),
    batch_size: int = Form(50)
):
    """
    Bulk enrich products from a CSV or Excel file
    
    Args:
        background_tasks: FastAPI background tasks
        file: CSV or Excel file with product data
        include_images: Whether to include images in the results
        batch_size: Number of products to process in each batch
        
    Returns:
        BulkEnrichmentResponse: Bulk enrichment task information
    """
    request_id = f"bulk-{int(time.time())}"

    try:
        # Read the uploaded file
        content = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(content))
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Only CSV or XLSX files are supported")

        # Validate required columns
        required_cols = ['mfg_part_number']
        for col in required_cols:
            if col not in df.columns:
                raise HTTPException(status_code=400, detail=f"Missing required column: {col}")

        # Limit rows to process
        total_rows = min(len(df), settings.MAX_ROWS_TO_PROCESS)
        logger.info(f"[{request_id}] Will process {total_rows} rows with batch size {batch_size}")

        # Initialize task tracking in background
        task_id = get_task_id()

        # Add the processing to background tasks
        # This will start processing after the response is sent
        background_tasks.add_task(
            process_bulk_file,
            df[:total_rows], 
            include_images, 
            min(batch_size, settings.MAX_BATCH_SIZE),
            task_id
        )

        return {
            "status": "processing",
            "task_id": task_id,
            "message": f"Processing {total_rows} rows in the background",
            "total_rows": total_rows,
            "estimated_time_seconds": total_rows * 2  # Rough estimate
        }

    except Exception as e:
        logger.error(f"[{request_id}] Error starting bulk process: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# -------------------- Main Entry Point --------------------

if __name__ == "__main__":
    import uvicorn
    
    # Ensure output directory exists
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    # Start the server
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)