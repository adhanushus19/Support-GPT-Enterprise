# Phase 7: Evaluation

## 🎯 Goals
Calculate metrics to verify output relevance and trust levels:
- **Faithfulness**: Are assertions supported by context?
- **Hallucination Rate**: What percentage of output represents unbacked details?
- **Context Precision & Recall**: Does search return appropriate context?

---

## ⚙️ Design Decisions
We write adapters (`ragas_eval.py`, `deepeval_eval.py`) that call real frameworks if API keys are set, otherwise fallback to local estimators using text comparisons.

---

## 💻 Code Walkthrough Reference
- Metric calculations: [framework.py](file:///C:/Users/adhan/.gemini/antigravity/scratch/supportgpt-enterprise/src/evaluation/framework.py).
- Evaluation console runner: [run_eval.py](file:///C:/Users/adhan/.gemini/antigravity/scratch/supportgpt-enterprise/scripts/run_eval.py).

---

## 🧪 Validation Steps
1. Run evaluation tests:
   ```bash
   python scripts/run_eval.py
   ```
2. Verify that the output report grid displays correct metrics for each query version.
3. Check generated JSON reports inside `evaluation/reports/`.
