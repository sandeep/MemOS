import json
from src.llm_utils import ask_llm
from src.evaluator import generate_answer_key, evaluate_file

with open("specs/test-case-conversation.json") as f:
    t = f.read()
key = generate_answer_key(t)
res, details = evaluate_file("output_propositional_kg.json", key)
for i, d in enumerate(details):
    print(f"\nQ{i+1}:")
    print(f"TRUTH: {d['truth']}")
    print(f"KG ANSWER: {d['answer']}")
    print(f"JUDGE SCORE: {d['score']}")
    print(f"JUDGE REASONING: {d.get('reasoning', 'N/A')}")
