import time
import os
import json
import logging
from typing import List, Dict, Any

from src.evaluation.ragas_eval import ragas_evaluator
from src.evaluation.deepeval_eval import deepeval_evaluator
from src.models.schemas import EvaluateResponseResponse

logger = logging.getLogger("supportgpt.evaluation.framework")

async def run_deeval_evaluation(
    query: str, context: List[str], response: str
) -> EvaluateResponseResponse:
    """
    Unified evaluation runner combining RAGAS and DeepEval metrics.
    Saves evaluations as JSON reports in evaluation/reports/.
    """
    start_time = time.time()
    
    # 1. Execute sub-evaluations
    ragas_scores = await ragas_evaluator.run_evaluation(query, context, response)
    deepeval_scores = await deepeval_evaluator.run_evaluation(query, context, response)

    # 2. Extract specific variables
    faithfulness = ragas_scores.get("faithfulness", 0.0)
    context_precision = ragas_scores.get("context_precision", 0.0)
    context_recall = ragas_scores.get("context_recall", 0.0)
    answer_relevance = deepeval_scores.get("answer_relevancy", 0.0)
    
    # Hallucination rate is the fraction of unsupported assertions
    hallucination_rate = deepeval_scores.get("hallucination_score", 0.0)

    # 3. Calculate overall quality score (average of relevance, faithfulness, precision, recall)
    metrics_sum = faithfulness + context_precision + context_recall + answer_relevance
    overall_quality = round(metrics_sum / 4.0, 2)
    
    # A response passes if quality is >= 0.80 and hallucination rate is low (< 0.30)
    passed = overall_quality >= 0.75 and hallucination_rate < 0.35

    report_summary = (
        f"Evaluation completed in {round(time.time() - start_time, 2)}s. "
        f"Overall Quality Score: {overall_quality}. Passed: {passed}. "
        f"Faithfulness: {faithfulness}, Hallucination Rate: {hallucination_rate}. "
        f"Context Precision: {context_precision}, Context Recall: {context_recall}."
    )

    # 4. Save report in reports directory
    report_data = {
        "timestamp": time.time(),
        "query": query,
        "context": context,
        "response": response,
        "metrics": {
            "faithfulness": faithfulness,
            "context_precision": context_precision,
            "context_recall": context_recall,
            "hallucination_rate": hallucination_rate,
            "answer_relevance": answer_relevance,
            "overall_quality_score": overall_quality
        },
        "passed": passed,
        "summary": report_summary
    }

    # Ensure reports directory exists
    reports_dir = os.path.join("evaluation", "reports")
    try:
        os.makedirs(reports_dir, exist_ok=True)
        report_path = os.path.join(reports_dir, f"report_{int(time.time())}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save evaluation report to disk: {e}")

    return EvaluateResponseResponse(
        faithfulness_score=faithfulness,
        context_precision=context_precision,
        context_recall=context_recall,
        hallucination_rate=hallucination_rate,
        answer_relevance=answer_relevance,
        overall_quality_score=overall_quality,
        passed_evaluation=passed,
        report_summary=report_summary
    )
