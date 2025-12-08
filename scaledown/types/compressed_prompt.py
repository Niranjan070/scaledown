from pydantic import BaseModel, computed_field
from typing import Tuple
from .metrics import CompressionMetrics

class CompressedPrompt(BaseModel):
    """
    A Pydantic model with structured, validated metrics.
    """
    content: str
    metrics: CompressionMetrics
    
    def __str__(self) -> str:
        return self.content
    
    def __repr__(self) -> str:
        return f"CompressedPrompt({len(self.content)} chars, {self.savings_percent:.1f}% saved)"
    
    @computed_field
    @property
    def tokens(self) -> Tuple[int, int]:
        return (self.metrics.original_prompt_tokens, 
                self.metrics.compressed_prompt_tokens)
    
    @computed_field
    @property
    def savings_percent(self) -> float:
        """Percentage of tokens removed (e.g., 60.0)."""
        orig = self.metrics.original_prompt_tokens
        comp = self.metrics.compressed_prompt_tokens
        if not orig:
            return 0.0
        return ((orig - comp) / orig) * 100

    @computed_field
    @property
    def compression_ratio(self) -> float:
        """Ratio of original to compressed size (e.g., 2.5)."""
        orig = self.metrics.original_prompt_tokens
        comp = self.metrics.compressed_prompt_tokens
        if not comp:
            return 0.0 
        return orig / comp
    
    @property
    def latency(self) -> int:
        return self.metrics.latency_ms
    
    def print_stats(self) -> None:
        print(f"ScaleDown Stats:")
        print(f"  - Tokens: {self.tokens[0]} -> {self.tokens[1]}")
        print(f"  - Savings: {self.savings_percent:.1f}%")
        print(f"  - Ratio: {self.compression_ratio:.1f}x")
        print(f"  - Latency: {self.latency}ms")
    
    @classmethod
    def from_api_response(cls, content: str, raw_response: dict) -> 'CompressedPrompt':
        # Safely extract metrics dictionary from response if nested
        metrics_data = raw_response.get('metrics', raw_response)
        
        metrics = CompressionMetrics(
            original_prompt_tokens=metrics_data.get('original_prompt_tokens', 0),
            compressed_prompt_tokens=metrics_data.get('compressed_prompt_tokens', 0),
            latency_ms=metrics_data.get('latency_ms', 0),
            timestamp=metrics_data.get('timestamp')
        )
        return cls(content=content, metrics=metrics)
