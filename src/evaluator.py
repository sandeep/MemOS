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

def generate_answer_key(transcript_str: str) -> list:
    print("\n--- PHASE 1: GENERATING ANSWER KEY ---")
    answer_key = []
    for i, q in enumerate(QUESTIONS):
        candidates = []
        for attempt in range(3):
            print(f"Generating Ground Truth for Q{i+1} (attempt {attempt+1}/3)...")
            prompt = f"Answer this question using the transcript below. Keep answers to 1 sentence. (Attempt {attempt+1}/3)\n\nQuestion:\n{q}\n\nTranscript:\n{transcript_str}"
            answer = call_llm(prompt).strip()
            candidates.append(answer)

        print(f"Synthesizing final Ground Truth for Q{i+1} from 3 attempts...")
        synth_prompt = (
            f"Given the question and 3 candidate answers generated from a transcript, synthesize or select the single most accurate, complete, and concise 1-sentence Ground Truth answer.\n\n"
            f"Question:\n{q}\n\n"
            f"Candidate 1: {candidates[0]}\n"
            f"Candidate 2: {candidates[1]}\n"
            f"Candidate 3: {candidates[2]}\n\n"
            f"Output ONLY the final 1-sentence Ground Truth answer."
        )
        final_answer = call_llm(synth_prompt).strip()
        if not final_answer and any(candidates):
            final_answer = next(c for c in candidates if c)
        answer_key.append(final_answer)
    return answer_key

def run_pipeline(transcript_file: str, kg_files: list):
    with open(transcript_file, 'r') as f:
        transcript_str = json.dumps(json.load(f))[:8000]
        
    answer_key = generate_answer_key(transcript_str)
    return answer_key

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 src/evaluator.py <transcript.json> <kg_file1.json> [kg_file2.json ...]")
        sys.exit(1)
    run_pipeline(sys.argv[1], sys.argv[2:])
