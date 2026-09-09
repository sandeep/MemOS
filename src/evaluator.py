import json
import requests
import sys
import re
import os

NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

def call_llm(prompt: str, model: str = "nvidia/nemotron-3-ultra-550b-a55b", temp: float = 0.0) -> str:
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        print("ERROR: NVIDIA_API_KEY not set.")
        return ""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temp,
        "max_tokens": 1024
    }
    try:
        response = requests.post(NVIDIA_URL, headers=headers, json=payload)
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"].strip()
        # Clean CoT
        if "Here's a thinking process:" in text:
            parts = text.split("\n\n")
            if len(parts) > 1:
                text = "\n\n".join(parts[1:]).strip()
        return text
    except Exception as e:
        print(f"LLM Error: {e}")
        return ""

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
