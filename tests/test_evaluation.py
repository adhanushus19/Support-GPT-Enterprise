import pytest
import os
from src.evaluation.hallucination import hallucination_evaluator
from src.evaluation.retrieval_metrics import retrieval_metrics_evaluator
from src.evaluation.response_metrics import response_metrics_evaluator
from src.evaluation.framework import run_deeval_evaluation

def test_hallucination_scorer():
    context = ["Corporate billing rules assert refunds are valid up to 30 days."]
    response_faithful = "According to corporate billing rules, refunds are valid for 30 days."
    response_hallucinated = "We refund all user payments up to 90 days and give a free coupon."
    
    faithful_rate = hallucination_evaluator.evaluate(context, response_faithful)
    hallucinated_rate = hallucination_evaluator.evaluate(context, response_hallucinated)
    
    assert faithful_rate < 0.2
    assert hallucinated_rate > 0.4

def test_retrieval_metrics():
    query = "configure account preferences email"
    context_relevant = ["To configure account settings, open Preferences and modify your email."]
    context_irrelevant = ["We offer delivery services via shipping carriers."]
    
    precision_rel = retrieval_metrics_evaluator.calculate_precision(query, context_relevant)
    precision_irrel = retrieval_metrics_evaluator.calculate_precision(query, context_irrelevant)
    
    assert precision_rel > 0.5
    assert precision_irrel == 0.0

def test_response_metrics():
    query = "billing refund invoice"
    response = "I can refund your billing invoice."
    
    relevance = response_metrics_evaluator.calculate_relevance(query, response)
    assert relevance > 0.5

@pytest.mark.asyncio
async def test_unified_evaluation_framework():
    query = "api outage devops"
    context = ["API outages are resolved by DevOps."]
    response = "API outages are resolved by DevOps."
    
    res = await run_deeval_evaluation(query, context, response)
    
    assert res.overall_quality_score >= 0.70
    assert res.passed_evaluation is True
    assert len(res.report_summary) > 0
    
    # Verify report was saved in evaluation/reports/
    reports_dir = os.path.join("evaluation", "reports")
    assert os.path.isdir(reports_dir)
    assert len(os.listdir(reports_dir)) > 0
