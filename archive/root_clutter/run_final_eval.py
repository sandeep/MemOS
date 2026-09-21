import json
import re
import sys
from src.llm_utils import call_llm
from src.evaluator import QUESTIONS, retrieve_answers, judge_answers

# Load answer key
with open("answer_key.json", "r") as f:
    answer_key = json.load(f)

files = ["output.json", "output_rlms.json", "output_propositional_kg.json"]
results = {}

print("Starting Evaluation...\n")
for kg_file in files:
    print(f"--- EVALUATING {kg_file} ---")
    try:
        with open(kg_file, 'r') as f:
            kg_str = json.dumps(json.load(f))
    except Exception as e:
        print(f"Error loading {kg_file}: {e}")
        continue
        
    retrieved = retrieve_answers(kg_str)
    scores = judge_answers(answer_key, retrieved)
    
    avg_score = sum(scores) / len(scores) if scores else 0
    results[kg_file] = avg_score
    for i, score in enumerate(scores):
        print(f"  Q{i+1} Score: {score}")
    print(f"Final Score for {kg_file}: {avg_score}%\n")

print("======================================")
print("FINAL LEADERBOARD:")
for file, score in results.items():
    print(f"{file}: {score}%")
print("======================================")
