from typing import Dict

# Pricing per 1,000 tokens in USD
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4": {
        "input": 0.03,
        "output": 0.06
    },
    "gpt-4-turbo": {
        "input": 0.01,
        "output": 0.03
    },
    "gpt-3.5-turbo": {
        "input": 0.0015,
        "output": 0.002
    },
    "mock": {
        "input": 0.0,
        "output": 0.0
    }
}

def calculate_llm_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate estimated cost in USD for LLM usage.
    """
    normalized_name = model_name.lower()
    
    # Matching logic
    matching_model = "mock"
    for key in sorted(MODEL_PRICING.keys(), key=len, reverse=True):
        if key in normalized_name:
            matching_model = key
            break
            
    rates = MODEL_PRICING[matching_model]
    input_cost = (input_tokens / 1000.0) * rates["input"]
    output_cost = (output_tokens / 1000.0) * rates["output"]
    
    return round(input_cost + output_cost, 6)
