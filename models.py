from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime

class LocationInput(BaseModel):
    """Input model for location data"""
    address: str = Field(..., description="Full address or location name")
    pincode: Optional[str] = Field(None, description="Postal/PIN code")
    city: Optional[str] = Field(None, description="City name")
    country: Optional[str] = Field(None, description="Country name")

class LocationData(BaseModel):
    """Processed location data with coordinates"""
    address: str
    pincode: Optional[str] = None
    latitude: float
    longitude: float
    city: Optional[str] = None
    country: Optional[str] = None

class RankingRequest(BaseModel):
    """Request model for ranking check"""
    keyword: str = Field(..., description="Keyword to track rankings for")
    location: LocationInput = Field(..., description="Location information")
    language_code: Optional[str] = Field("en", description="Language code (e.g., 'en', 'es')")
    device: Optional[Literal["desktop", "mobile"]] = Field("desktop", description="Device type")
    depth: Optional[int] = Field(40, description="Number of results to fetch", ge=1, le=100)

    @validator('keyword')
    def keyword_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Keyword cannot be empty')
        return v.strip()

class OrganicResult(BaseModel):
    """Organic search result model"""
    position: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    domain: Optional[str] = None
    breadcrumb: Optional[str] = None

class MapResult(BaseModel):
    """Map search result model"""
    position: Optional[int] = None
    title: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    category: Optional[str] = None

class RankingResults(BaseModel):
    """Response model for ranking results"""
    keyword: str
    location: LocationData
    device: str
    language_code: str
    depth: int
    organic_results: List[OrganicResult]
    maps_results: List[MapResult]
    check_date: datetime
    processing_time_seconds: Optional[float] = None

class BulkRankingRequest(BaseModel):
    """Request model for bulk ranking checks"""
    keywords: List[str] = Field(..., description="List of keywords to track")
    location: LocationInput = Field(..., description="Location information")
    language_code: Optional[str] = Field("en", description="Language code")
    device: Optional[Literal["desktop", "mobile"]] = Field("desktop", description="Device type")
    depth: Optional[int] = Field(40, description="Number of results to fetch")

class RankingSummary(BaseModel):
    """Summary statistics for ranking results"""
    total_keywords: int
    average_organic_position: Optional[float] = None
    average_maps_position: Optional[float] = None
    organic_visibility: float = 0.0  # Percentage of keywords ranking in organic
    maps_visibility: float = 0.0     # Percentage of keywords ranking in maps

class APIStatus(BaseModel):
    """API status response model"""
    service: str
    status: str
    response_time_ms: Optional[float] = None
    last_check: datetime

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    details: Optional[str] = None