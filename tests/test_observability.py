import pytest
from src.observability.token_tracking import estimate_tokens
from src.observability.cost_tracking import calculate_llm_cost
from src.observability.metrics import LLM_TOKENS_TOTAL

def test_token_estimation():
    assert estimate_tokens("") == 0
    assert estimate_tokens("hello") > 0
    # Approx 4 characters per token check
    assert estimate_tokens("hello world supportgpt") == len("hello world supportgpt") // 4

def test_cost_calculation():
    # gpt-4 cost: $0.03 input, $0.06 output per 1k tokens
    cost = calculate_llm_cost("gpt-4", 1000, 1000)
    assert cost == 0.09
    
    # gpt-4-turbo cost: $0.01 input, $0.03 output per 1k tokens
    cost_turbo = calculate_llm_cost("gpt-4-turbo", 1000, 1000)
    assert cost_turbo == 0.04
    
    # Mock cost: $0
    cost_mock = calculate_llm_cost("mock", 1000, 1000)
    assert cost_mock == 0.0

def test_prometheus_metrics_registry():
    # Verify metric label dimensions are defined
    assert "model" in LLM_TOKENS_TOTAL._labelnames
    assert "type" in LLM_TOKENS_TOTAL._labelnames
