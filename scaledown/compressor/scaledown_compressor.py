import requests
from typing import Union, List, Optional
from concurrent.futures import ThreadPoolExecutor

from .base import BaseCompressor
from ..exceptions import AuthenticationError, APIError
from ..types import CompressedPrompt

class ScaleDownCompressor(BaseCompressor):
    """
    Standard ScaleDown compressor using the hosted model on API.
    """
    # UPDATED: Correct endpoint from documentation
    BASE_URL = "https://api.scaledown.xyz/compress/raw/"

    def __init__(self, target_model='gpt-4o', rate='auto', api_key=None, 
                 temperature=None, preserve_keywords=False, preserve_words=None):
        super().__init__(rate=rate, api_key=api_key)
        self.target_model = target_model
        self.temperature = temperature
        self.preserve_keywords = preserve_keywords
        self.preserve_words = preserve_words or []

    def compress(self, context: Union[str, List[str]], prompt: Union[str, List[str]], 
                 max_tokens: int = None, **kwargs) -> Union[CompressedPrompt, List[CompressedPrompt]]:
        """
        Compress context using ScaleDown's hosted API.
        """
        if isinstance(context, str) and isinstance(prompt, str):
            return self._compress_single(context, prompt, max_tokens=max_tokens, **kwargs)
        
        elif isinstance(context, list) and isinstance(prompt, list):
            if len(context) != len(prompt):
                raise ValueError("Context list and prompt list must have the same length.")
            return self._compress_batch(context, prompt, max_tokens=max_tokens, **kwargs)
            
        elif isinstance(context, list) and isinstance(prompt, str):
            # Broadcast prompt to all contexts
            return self._compress_batch(context, [prompt] * len(context), max_tokens=max_tokens, **kwargs)
        
        else:
            raise ValueError("Invalid combination of context and prompt types.")

    def _compress_batch(self, context_list, prompt_list, **kwargs):
        # Using 5 workers as per design
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(
                lambda p: self._compress_single(p[0], p[1], **kwargs), 
                zip(context_list, prompt_list)
            ))
        return results

    def _compress_single(self, context, prompt, max_tokens=None, **kwargs) -> CompressedPrompt:
        if not self.api_key:
            raise AuthenticationError("API key not found. Use scaledown.set_api_key() or pass api_key to constructor.")

        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

        #Payload structure that matches documentation (nested 'scaledown' object)
        payload = {
            "context": context,
            "prompt": prompt,
            "model": self.target_model,
            "scaledown": {
                "rate": self.rate,
                "temperature": self.temperature,
                "preserve_keywords": self.preserve_keywords,
                "preserve_words": self.preserve_words,
                "max_tokens": max_tokens,
                **kwargs
            }
        }

        try:
            response = requests.post(
                 self.BASE_URL,
                 headers=headers,
                 json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            # --- FIX: Extract nested data ---
            results = data.get("results", {})
            
            # 1. Get content from 'results'
            content = results.get("compressed_prompt", "")
            
            # 2. Map API keys to our internal Metrics names
            # The API uses 'total_original_tokens', our Metrics class expects 'original_prompt_tokens'
            prepared_metrics = {
                "original_prompt_tokens": data.get("total_original_tokens", results.get("original_prompt_tokens", 0)),
                "compressed_prompt_tokens": data.get("total_compressed_tokens", results.get("compressed_prompt_tokens", 0)),
                "latency_ms": data.get("latency_ms", 0),
                "model_used": data.get("model_used"),
                "timestamp": data.get("request_metadata", {}).get("timestamp")
            }
            
            return CompressedPrompt.from_api_response(
                content=content, 
                raw_response=prepared_metrics 
            )

        except requests.exceptions.RequestException as e:
            raise APIError(f"Connection failed: {str(e)}")
