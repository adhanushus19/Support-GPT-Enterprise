import tiktoken
from typing import Optional

def estimate_tokens(text: Optional[str]) -> int:
    """
    Estimate token counts for a given text block.
    Uses tiktoken cl100k_base if available, otherwise falls back to character-ratio heuristics.
    """
    if not text:
        return 0
    
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        # Fallback heuristic: 1 token ~ 4 characters
        return max(1, len(text) // 4)
