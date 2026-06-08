import os
import sys
import asyncio

# Ensure project root is in path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database import init_db, AsyncSessionLocal
from src.agents.graph import run_agent_workflow
from src.evaluation.framework import run_deeval_evaluation

EVAL_TESTS = [
    {
        "query": "I would like to get a refund for my billing invoice paid 10 days ago.",
        "kb_version": "v1"
    },
    {
        "query": "Our systems are experiencing 504 errors on API endpoints. Is it down?",
        "kb_version": "v1"
    },
    {
        "query": "How do I configure my account settings profile details?",
        "kb_version": "v1"
    },
    {
        "query": "I want a refund for an invoice paid 50 days ago. Can I get it?",
        "kb_version": "v2" # Test v2 refund policy rules
    }
]

async def run_pipeline_evaluation():
    print("Initializing tables...")
    await init_db()
    
    reports = []
    print("\nStarting SupportGPT Enterprise RAG/Agent Pipeline Evaluation...\n")

    for i, test in enumerate(EVAL_TESTS):
        print(f"--- Running Test Case {i+1} ---")
        print(f"Query: {test['query']}")
        print(f"KB Version: {test['kb_version']}")

        # 1. Execute agent graph workflow to get response and context citations
        initial_state = {
            "ticket_id": 900 + i,
            "customer_id": f"cust_eval_{i}",
            "subject": f"Evaluation ticket {i}",
            "description": test["query"],
            "kb_version": test["kb_version"]
        }
        
        agent_output = await run_agent_workflow(initial_state)
        response = agent_output.get("suggested_response", "")
        citations = agent_output.get("context_citations", [])
        context_texts = [c.text for c in citations]

        print(f"Generated Response: {response}")
        print(f"Retrieved {len(citations)} citations.")

        # 2. Run Evaluation metrics
        print("Computing quality metrics...")
        eval_result = await run_deeval_evaluation(
            query=test["query"],
            context=context_texts,
            response=response
        )

        reports.append({
            "query": test["query"],
            "version": test["kb_version"],
            "overall_quality": eval_result.overall_quality_score,
            "faithfulness": eval_result.faithfulness_score,
            "hallucination": eval_result.hallucination_rate,
            "relevance": eval_result.answer_relevance,
            "passed": eval_result.passed_evaluation
        })
        print(f"Result: {eval_result.report_summary}\n")

    # Display final report matrix
    print("="*80)
    print(f"{'EVALUATION REPORT SUMMARY MATRIX':^80}")
    print("="*80)
    print(f"{'Query Snippet':<30} | {'Ver':<3} | {'Quality':<7} | {'Faith':<5} | {'Halluc':<6} | {'Relev':<5} | {'Pass':<4}")
    print("-"*80)
    for rep in reports:
        snippet = rep["query"][:27] + "..." if len(rep["query"]) > 27 else rep["query"]
        print(f"{snippet:<30} | {rep['version']:<3} | {rep['overall_quality']:<7} | {rep['faithfulness']:<5} | {rep['hallucination']:<6} | {rep['relevance']:<5} | {str(rep['passed']):<4}")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(run_pipeline_evaluation())
