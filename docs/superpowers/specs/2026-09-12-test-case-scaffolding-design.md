# Spec: Test Case Scaffolding & PII Architecture

## 1. Overview
The current evaluation pipeline is hardcoded and unstructured, leaving raw transcripts, extracted KGs, and evaluation artifacts cluttered in root or `specs/` directories. Furthermore, there is no structural boundary protecting PII-laden transcripts from intermediate LLM logs.

This design introduces a formal "Test Case Orchestrator" that groups files by conversation name and establishes a strict physical directory boundary between secure user data and intermediate working files.

## 2. Directory Architecture

The system splits data into two distinct security zones:

```text
data/
  ├── secure/                             
  │   ├── inputs/
  │   │   └── interview_01.json               
  │   └── reconstituted/
  │       └── interview_01/
  │           ├── kg_naive_2026-09-12_gemma4.json
  │           ├── kg_rlms_2026-09-12_gemma4.json
  │           └── kg_propositional_2026-09-12_gemma4.json
  │
  └── working/                            
      ├── scrubbed_inputs/                
      │   └── interview_01.json           
      └── evaluations/            
          └── interview_01/               
              ├── answer_key.json                           <-- Ground truth (Run once, shared)
              ├── kg_naive_2026-09-12_gemma4.json           
              ├── kg_rlms_2026-09-12_gemma4.json            
              ├── kg_propositional_2026-09-12_gemma4.json   
              └── leaderboard_2026-09-12_gemma4.md          <-- Saved locally
```

## 3. The Orchestrator Interface

A single `run_pipeline.py` script orchestrates the end-to-end flow.

### Execution Modes
- **Targeted:** `python run_pipeline.py data/secure/interview_01.json`
- **Batch:** `python run_pipeline.py --all` (Scans `data/secure/` for un-evaluated JSON files).

### Pipeline Flow
1. **PII Scrubbing Phase:** Reads the raw file from `data/secure/`. For Phase 1 implementation, it simply passes the text through to `data/working/scrubbed_inputs/` to establish the architecture. (Future: Presidio NLP extraction mapping).
2. **Extraction Phase:** The script automatically runs all three extractors (Naive, RLM, and Propositional) using the scrubbed input. It enforces consistent naming for the outputs (`kg_naive.json`, `kg_rlms.json`, `kg_propositional.json`) and writes them into the `working/evaluations/[name]/` directory.
3. **Evaluation Phase:** 
   - Checks if `answer_key.json` exists in the evaluation directory. If not, generates it from the scrubbed input and caches it.
   - Tests all three extracted KGs against the answer key.
   - Outputs the final comparative leaderboard to the terminal.
4. **Reconstitution Phase:** (Future Placeholder) The winning KG is passed back across the boundary to have its PII injected, creating the `_reconstituted.json` file in `secure/`.

## 4. Immediate Implementation Scope
- Create the scaffolding directories.
- Refactor `src/evaluator.py` and the extractors to accept paths dynamically based on this structure.
- Write the `run_pipeline.py` orchestrator.
- Implement the "Passthrough" PII phase to ensure the architecture is functional before introducing the complex Presidio mapping logic.
