from pydantic import BaseModel, HttpUrl, field_validator


class ExtractRequest(BaseModel):
    """Request model for content extraction endpoint"""
    
    url: HttpUrl
    
    @field_validator('url')
    @classmethod
    def validate_url_scheme(cls, v):
        """Ensure URL uses http or https protocol"""
        if v.scheme not in ['http', 'https']:
            raise ValueError('URL must use http or https protocol')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/article"
            }
        }


