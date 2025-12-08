import scaledown as sd
from scaledown.compressor import ScaleDownCompressor
import os

# Set your key
API_KEY = "yVlJ8qWWVF6wj8RZUfNHm7fUYqNBVEFr3Rrfep67" # The key you pasted before
sd.set_api_key(API_KEY)

print(f"Testing ScaleDown API with key: {API_KEY[:5]}...")

compressor = ScaleDownCompressor(target_model="gpt-4o", rate="auto")

context_text = """
ScaleDown is an intelligent prompt compression service that reduces your AI token usage 
while preserving the semantic meaning of your prompts. Think of it as a smart compression 
tool for your AI conversations. You get the same quality responses while paying significantly less.
"""

try:
    print("\nSending request...")
    result = compressor.compress(
        context=context_text, 
        prompt="What is ScaleDown?"
    )
    
    print("\n--- Success! ---")
    print(f"Compressed Output: {str(result)}")
    print("\nMetrics:")
    result.print_stats()
    
except Exception as e:
    print(f"\n Error: {e}")
