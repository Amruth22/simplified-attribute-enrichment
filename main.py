"""
Simplified Attribute Enrichment - Main Application Entry Point
"""
import time
import logging
import traceback
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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

# -------------------- Error Handling --------------------

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# -------------------- API Routes --------------------

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "config": {
            "host": settings.HOST,
            "port": settings.PORT,
            "google_api_configured": bool(settings.GOOGLE_API_KEY and settings.GOOGLE_CSE_ID),
            "gemini_project": settings.GEMINI_PROJECT_ID,
            "gemini_model": settings.GEMINI_MODEL,
            "token_tracking_enabled": settings.ENABLE_TOKEN_TRACKING
        }
    }

@app.post("/api/v1/enrich", response_model=EnrichmentResponse)
async def enrich_product(
    request: EnrichmentRequest,
    debug: bool = Query(False, description="Enable debug mode with more detailed response")
):
    """
    Enrich a single product with attribute data and optionally images
    
    Args:
        request: Product enrichment request
        debug: Enable debug mode
        
    Returns:
        EnrichmentResponse: Enriched product data
    """
    request_id = f"single-{int(time.time())}"
    
    try:
        # Log the request in debug mode
        if debug:
            logger.info(f"[{request_id}] Debug mode enabled")
            logger.info(f"[{request_id}] Request: {request.dict()}")
        
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
        
        # In non-debug mode, remove raw Gemini response to reduce response size
        if not debug and "raw_gemini_response" in result:
            del result["raw_gemini_response"]
        
        return result
        
    except Exception as e:
        logger.error(f"[{request_id}] Error enriching product: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error enriching product: {str(e)}")

@app.post("/api/v1/bulk-enrich", response_model=BulkEnrichmentResponse)
async def bulk_enrich(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    include_images: bool = Form(False),
    batch_size: int = Form(50),
    debug: bool = Form(False, description="Enable debug mode with more detailed logging")
):
    """
    Bulk enrich products from a CSV or Excel file
    
    Args:
        background_tasks: FastAPI background tasks
        file: CSV or Excel file with product data
        include_images: Whether to include images in the results
        batch_size: Number of products to process in each batch
        debug: Enable debug mode
        
    Returns:
        BulkEnrichmentResponse: Bulk enrichment task information
    """
    request_id = f"bulk-{int(time.time())}"

    try:
        # Read the uploaded file
        content = await file.read()
        
        # Log file info in debug mode
        if debug:
            logger.info(f"[{request_id}] Debug mode enabled")
            logger.info(f"[{request_id}] File name: {file.filename}, Size: {len(content)} bytes")
        
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

        # Log dataframe info in debug mode
        if debug:
            logger.info(f"[{request_id}] DataFrame columns: {list(df.columns)}")
            logger.info(f"[{request_id}] DataFrame shape: {df.shape}")
            
            # Check for attributes_to_extract column
            if 'attributes_to_extract' in df.columns:
                sample = df['attributes_to_extract'].iloc[0] if not df.empty else None
                logger.info(f"[{request_id}] Sample attributes_to_extract: {sample}")
            else:
                logger.warning(f"[{request_id}] No 'attributes_to_extract' column found in the input file")

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
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# -------------------- Debug Endpoints --------------------

@app.get("/api/v1/debug/config")
async def debug_config():
    """Debug endpoint to view current configuration"""
    return {
        "api_settings": {
            "host": settings.HOST,
            "port": settings.PORT
        },
        "google_api": {
            "api_key_configured": bool(settings.GOOGLE_API_KEY),
            "cse_id_configured": bool(settings.GOOGLE_CSE_ID)
        },
        "gemini_api": {
            "project_id": settings.GEMINI_PROJECT_ID,
            "location": settings.GEMINI_LOCATION,
            "model": settings.GEMINI_MODEL
        },
        "processing_settings": {
            "max_batch_size": settings.MAX_BATCH_SIZE,
            "max_rows_to_process": settings.MAX_ROWS_TO_PROCESS,
            "token_tracking_enabled": settings.ENABLE_TOKEN_TRACKING
        },
        "file_paths": {
            "taxonomy_path": settings.TAXONOMY_PATH,
            "output_dir": settings.OUTPUT_DIR
        }
    }

# -------------------- Main Entry Point --------------------

if __name__ == "__main__":
    import uvicorn
    
    # Ensure output directory exists
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    
    # Start the server
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)