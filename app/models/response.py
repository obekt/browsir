from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ArticleContent(BaseModel):
    """Article content data model"""
    
    title: str
    body: str
    images: List[str]
    url: str
    extracted_at: datetime


class ExtractResponse(BaseModel):
    """Response model for content extraction endpoint"""
    
    success: bool
    data: Optional[ArticleContent] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "title": "Example Article",
                    "body": "Article content here...",
                    "images": ["https://example.com/image.jpg"],
                    "url": "https://example.com/article",
                    "extracted_at": "2025-11-04T08:00:00Z"
                }
            }
        }


