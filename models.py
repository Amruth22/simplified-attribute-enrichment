"""
Data models for the Simplified Attribute Enrichment service
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

# -------------------- Request Models --------------------

class EnrichmentRequest(BaseModel):
    """Request model for product enrichment"""
    mpn: str = Field(..., description="Manufacturer part number")
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    category: Optional[str] = Field(None, description="Product category")
    subcategory: Optional[str] = Field(None, description="Product subcategory")
    attributes_to_extract: Optional[List[str]] = Field(None, description="List of attributes to extract")
    include_images: bool = Field(True, description="Whether to include images in the response")

# -------------------- Response Models --------------------

class TokenData(BaseModel):
    """Token usage and cost data"""
    input_tokens: int = Field(0, description="Number of input tokens")
    output_tokens: int = Field(0, description="Number of output tokens")
    total_tokens: int = Field(0, description="Total number of tokens")
    cost_inr: float = Field(0.0, description="Cost in INR")

class EnrichmentResponse(BaseModel):
    """Response model for product enrichment"""
    mpn: str = Field(..., description="Manufacturer part number")
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    category: Optional[str] = Field(None, description="Product category")
    subcategory: Optional[str] = Field(None, description="Product subcategory")
    image_url: Optional[str] = Field(None, description="URL of the product image")
    attributes: Dict[str, Any] = Field({}, description="Extracted product attributes")
    processing_time_seconds: float = Field(0.0, description="Processing time in seconds")
    confidence: str = Field("LOW", description="Confidence level of the extraction")
    requested_attributes: List[str] = Field([], description="List of requested attributes")
    token_data: TokenData = Field(default_factory=TokenData, description="Token usage and cost data")
    raw_gemini_response: Optional[str] = Field(None, description="Raw response from Gemini API")

class BulkEnrichmentResponse(BaseModel):
    """Response model for bulk enrichment"""
    status: str = Field(..., description="Status of the bulk enrichment")
    task_id: str = Field(..., description="Task ID for tracking")
    message: str = Field(..., description="Status message")
    total_rows: int = Field(..., description="Total number of rows to process")
    estimated_time_seconds: int = Field(..., description="Estimated processing time in seconds")

# -------------------- Internal Models --------------------

class ImageResult(BaseModel):
    """Model for image search results"""
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    source_url: Optional[str] = None
    manufacturer_match: bool = False
    confidence: str = "LOW"

class GeminiResponse(BaseModel):
    """Model for Gemini API response data"""
    text: str
    tokens: Dict[str, int]
    costs: Dict[str, Any]

# -------------------- Global State --------------------

class TokenStats:
    """Global token statistics tracker"""
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost_inr: float = 0.0
    
    def reset(self):
        """Reset all token statistics"""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_inr = 0.0
    
    def update(self, input_tokens: int, output_tokens: int, cost_inr: float):
        """Update token statistics"""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost_inr += cost_inr
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current token statistics"""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost_inr": self.total_cost_inr
        }

# Global token stats instance
token_stats = TokenStats()