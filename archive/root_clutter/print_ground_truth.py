import json
import sys
from src.evaluator import generate_answer_key, QUESTIONS

with open("specs/test-case-conversation.json", 'r') as f:
    transcript_str = json.dumps(json.load(f))[:8000]

print("Fetching Answer Key...")
# Run the answer key logic
answer_key = generate_answer_key(transcript_str)

for i, (q, a) in enumerate(zip(QUESTIONS, answer_key)):
    print(f"\nQuestion {i+1}: {q}")
    print(f"Ground Truth: {a}")
