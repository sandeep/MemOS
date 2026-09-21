# DSPy Algorithmic Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pivot from manually tuning Cognitive Graph prompts to using DSPy to algorithmically discover the optimal prompt instructions and few-shot examples for extracting long-context conversational state into structured JSON.

**Architecture:** We will wrap our existing `generate_rubric.py` and `evaluator.py` output (the 15-question mechanical LLM Judge) into a formal DSPy `Metric` function. We will then define a DSPy `Signature` for `Transcript -> CognitiveGraph`. Finally, we will run the `MIPRO` (or `BootstrapFewShotWithRandomSearch`) teleprompter to automatically compile the V3 prompt against our 100 ShareGPT files.

**Tech Stack:** Python 3, DSPy, existing pipeline metrics (`src/evaluator.py`).

## Global Constraints

- **Cache Refactor First:** The old MD5 cache logic must be migrated to semantic `task_id` logging *before* running DSPy, or the teleprompter will burn excessive API credits.
- **Metric Integrity:** The custom DSPy metric must exactly mirror the mathematical grading logic (F1 / LLM Judge percentage) developed in our earlier iterations.
- **Holdout Set:** We must partition the 100 ShareGPT files into train/dev/test sets (e.g., 60/20/20) to prevent the DSPy optimizer from overfitting the instructions.

---

### Task 1: Execute Cache Refactoring

- [ ] Write `migrate_cache.py` to reconstruct the exact prompts for the 2,400+ MD5 hashes in `llm_cache/` and rename them to `{dataset}_{file_id}_{task}.txt`.
- [ ] Refactor `src/llm_utils.py` `call_llm()` to accept an explicit `task_id` argument and strictly write to `llm_cache/{task_id}.txt`.
- [ ] Update `generate_rubric.py`, `evaluator.py`, and `extractor_recursive.py` to pass the correct human-readable `task_id` strings to `call_llm()`.
- [ ] Remove the redundant `.raw.txt` fallback patches, as the cache is now perfectly human-readable.

### Task 2: Ground Truth Generation (Scale Up)

- [ ] Execute `run_sharegpt_safe.sh` (or equivalent orchestrator) across all 100 ShareGPT files *specifically* to generate and cache the 15-question rubrics and Ground Truth answer keys.
- [ ] Validate that all 100 `answer_key.json` files exist so that the DSPy metric function can evaluate candidate graphs with zero latency and low API cost.

### Task 3: DSPy Setup & Signature Definition

- [ ] Install DSPy (`pip install dspy-ai`).
- [ ] Create `src/dspy_optimizer.py`.
- [ ] Configure DSPy to use our local OpenRouter `call_llm()` logic or configure DSPy's native `LM` class with our API keys and guardrails.
- [ ] Define the DSPy Signature: `class ExtractCognitiveGraph(dspy.Signature): ...` with the `transcript` as input and the `cognitive_graph_json` as output.

### Task 4: Metric Integration & Compilation

- [ ] Write a DSPy `Metric` wrapper function that takes the predicted `cognitive_graph_json`, loads the cached `ground_truth_answer_key.json` for that specific transcript, and runs our `evaluator.py` LLM Judge logic.
- [ ] Initialize the DSPy optimizer (e.g., `teleprompter = dspy.MIPRO(metric=llm_judge_metric)`).
- [ ] Compile the program using the training split of the 100 ShareGPT files.
- [ ] Save the optimized DSPy program (the JSON/YAML compiled state) to `data/secure/dspy_compiled_v3.json`.

### Task 5: Final Evaluation vs Naive V2

- [ ] Run the freshly compiled, DSPy-optimized Cognitive Graph extractor on the holdout test set (the final 20 ShareGPT files).
- [ ] Compare its average score against the `Naive V2` (raw text summary) baseline.
- [ ] If the DSPy-optimized structured JSON still fails to beat `Naive V2`, document the scientific conclusion and officially pivot the cognitive architecture away from strict JSON graphs.
