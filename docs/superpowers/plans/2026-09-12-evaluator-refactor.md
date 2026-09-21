# Evaluator Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the LLM Judge evaluation script into a 3-stage RAG pipeline: (1) Answer Key Generation, (2) Retriever, (3) LLM Judge, capable of scoring multiple Knowledge Graphs.

**Architecture:** We will rewrite `src/evaluator.py`. It will first take a raw transcript and generate the "Ground Truth" Answer Key for a static list of taxonomy questions. Then, it will iterate through one or more provided KG files (`output.json`, `output_rlms.json`, etc.), use a Retriever prompt to answer the same questions, and finally use an LLM Judge prompt to score the retrieved answers against the Ground Truth.

**Tech Stack:** Python, `llm_utils.py`

---

### Task 1: Refactor CLI and Basic Structure

**Files:**
- Modify: `src/evaluator.py`

- [ ] **Step 1: Write the failing test / setup execution**
Since this is an evaluation script, we will test it by running it with a mock LLM or against actual files. We don't have pytest setup, so we will use manual script execution.
Run: `python3 src/evaluator.py specs/test-case-conversation.json output.json`
(Currently it works but uses the old logic. We will replace it.)

- [ ] **Step 2: Rewrite the imports, questions list, and main CLI**
Replace the entire `src/evaluator.py` content to establish the new architecture shell.

```python
"""
evaluator.py
3-Stage Evaluator: (1) Answer Key (2) Retriever (3) Judge
Scores multiple KG files against a raw transcript.
"""
import json
import sys
import re
from llm_utils import call_llm

QUESTIONS = [
    "(Control) The user begins their message with a self-description that includes a specific personality identifier and two adjectives; what is the exact string the user uses for their personality type and cognitive style?",
    "(Semantic) What is the core conflict or objective vs subjective tension expressed by the user regarding taste-based professions?",
    "(Episodic) What is the sequence of logical steps the AI takes to reframe 'taste' as a data processing system for the user?",
    "(Procedural/Active) What is the immediate focus or unresolved question the AI is trying to address to bridge the gap for the user?"
]

def run_pipeline(transcript_file: str, kg_files: list):
    pass

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 src/evaluator.py <transcript.json> <kg_file1.json> [kg_file2.json ...]")
        sys.exit(1)
    run_pipeline(sys.argv[1], sys.argv[2:])
```

- [ ] **Step 3: Commit**
```bash
git add src/evaluator.py
git commit -m "refactor: setup 3-stage evaluator CLI structure"
```

### Task 2: Implement Answer Key Generation (Baseline)

**Files:**
- Modify: `src/evaluator.py`

- [ ] **Step 1: Implement `generate_answer_key`**
Add the answer key generator function above `run_pipeline`.

```python
def generate_answer_key(transcript_str: str) -> list:
    print("\n--- PHASE 1: GENERATING ANSWER KEY ---")
    answer_key = []
    for i, q in enumerate(QUESTIONS):
        print(f"Generating Ground Truth for Q{i+1}...")
        prompt = f"Answer this question using the transcript below. Keep answers to 1 sentence.\n\nQuestion:\n{q}\n\nTranscript:\n{transcript_str}"
        answer = call_llm(prompt).strip()
        answer_key.append(answer)
    return answer_key
```

- [ ] **Step 2: Update `run_pipeline` to use it**

```python
def run_pipeline(transcript_file: str, kg_files: list):
    with open(transcript_file, 'r') as f:
        transcript_str = json.dumps(json.load(f))[:8000]
        
    answer_key = generate_answer_key(transcript_str)
```

- [ ] **Step 3: Commit**
```bash
git add src/evaluator.py
git commit -m "feat: implement baseline answer key generation"
```

### Task 3: Implement Retriever and Judge

**Files:**
- Modify: `src/evaluator.py`

- [ ] **Step 1: Implement `retrieve_answers` and `judge_answers`**
Add these functions above `run_pipeline`.

```python
def retrieve_answers(kg_str: str) -> list:
    retrieved = []
    for i, q in enumerate(QUESTIONS):
        prompt = f"Answer this question using ONLY the Knowledge Graph below. Keep answers to 1 sentence. If the info is missing, say 'MISSING'.\n\nQuestion:\n{q}\n\nKnowledge Graph:\n{kg_str}"
        ans = call_llm(prompt).strip()
        retrieved.append(ans)
    return retrieved

def judge_answers(answer_key: list, retrieved: list) -> list:
    scores = []
    for i, (base_ans, retr_ans) in enumerate(zip(answer_key, retrieved)):
        prompt = f"Compare the TRUE Answer to the Retrieved Answer. Did the Retrieved Answer miss any critical facts? Give a score out of 100 as a SINGLE INTEGER ONLY on the first line, followed by a 1-sentence explanation on the next line.\n\nTRUE Answer:\n{base_ans}\n\nRetrieved Answer:\n{retr_ans}"
        resp = call_llm(prompt).strip()
        
        try:
            score_match = re.search(r'\d+', resp)
            score = int(score_match.group()) if score_match else 0
        except:
            score = 0
        scores.append(score)
    return scores
```

- [ ] **Step 2: Complete `run_pipeline` execution loop**
Modify `run_pipeline` to loop through all provided KG files.

```python
def run_pipeline(transcript_file: str, kg_files: list):
    with open(transcript_file, 'r') as f:
        transcript_str = json.dumps(json.load(f))[:8000]
        
    answer_key = generate_answer_key(transcript_str)
    
    results = {}
    for kg_file in kg_files:
        print(f"\n--- PHASE 2 & 3: EVALUATING {kg_file} ---")
        try:
            with open(kg_file, 'r') as f:
                kg_str = json.dumps(json.load(f))
        except FileNotFoundError:
            print(f"File {kg_file} not found. Skipping.")
            continue
            
        retrieved = retrieve_answers(kg_str)
        scores = judge_answers(answer_key, retrieved)
        
        avg_score = sum(scores) / len(scores) if scores else 0
        results[kg_file] = avg_score
        print(f"Final Score for {kg_file}: {avg_score}%")
        
    print("\n======================================")
    print("FINAL LEADERBOARD:")
    for file, score in results.items():
        print(f"{file}: {score}%")
    print("======================================")
```

- [ ] **Step 3: Commit**
```bash
git add src/evaluator.py
git commit -m "feat: complete retriever, judge, and scoring pipeline"
```
