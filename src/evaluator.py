import json
import sys
import re
import os
from llm_utils import call_llm

def run_llm_judge(transcript_file: str, kg_file: str):
    with open(transcript_file, 'r') as f:
        transcript = json.load(f)
    with open(kg_file, 'r') as f:
        kg = json.load(f)
        
    transcript_str = json.dumps(transcript)[:8000]
    kg_str = json.dumps(kg)
    
    print("1. Generating questions from full context...")
    q_prompt = f"Read this transcript and generate 3 highly specific factual questions that can ONLY be answered if you read it closely. Output ONLY the 3 questions, numbered.\n\nTranscript: {transcript_str}"
    questions = call_llm(q_prompt)
    print(f"Questions:\n{questions}\n")
    
    print("2. Answering using FULL context (Baseline)...")
    base_prompt = f"Answer these questions using the transcript below. Keep answers to 1 sentence.\n\nQuestions:\n{questions}\n\nTranscript:\n{transcript_str}"
    base_answers = call_llm(base_prompt)
    print(f"Baseline Answers:\n{base_answers}\n")
    
    print("3. Answering using ONLY Extracted KG (Test)...")
    test_prompt = f"Answer these questions using ONLY the Knowledge Graph below. Keep answers to 1 sentence. If the info is missing, say 'MISSING'.\n\nQuestions:\n{questions}\n\nKnowledge Graph:\n{kg_str}"
    test_answers = call_llm(test_prompt)
    print(f"KG Answers:\n{test_answers}\n")
    
    print("4. Judging the delta...")
    judge_prompt = f"Compare the Baseline Answers to the KG Answers. Did the KG Answers miss any critical facts? Give a score out of 100% and a 2-sentence explanation.\n\nBaseline:\n{base_answers}\n\nKG:\n{test_answers}"
    score = call_llm(judge_prompt)
    print(f"FINAL SCORE:\n{score}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 src/evaluator.py <transcript.json> <output_kg.json>")
    else:
        run_llm_judge(sys.argv[1], sys.argv[2])
