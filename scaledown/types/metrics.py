from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class CompressionMetrics(BaseModel):
    """Validated metrics from the compression API."""
    original_prompt_tokens: int = 0
    compressed_prompt_tokens: int = 0
    latency_ms: int = 0
    timestamp: Optional[datetime] = None
    
    @field_validator('original_prompt_tokens', 'compressed_prompt_tokens', 'latency_ms')
    @classmethod
    def validate_positive(cls, v: int) -> int:
        if v < 0:
            raise ValueError('Must be non-negative')
        return v
