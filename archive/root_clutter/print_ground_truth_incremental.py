import json
import sys
from src.llm_utils import call_llm
from src.evaluator import QUESTIONS

with open("specs/test-case-conversation.json", 'r') as f:
    transcript_str = json.dumps(json.load(f))[:8000]

for i, q in enumerate(QUESTIONS):
    print(f"\nQuestion {i+1}: {q}")
    candidates = []
    for attempt in range(3):
        prompt = f"Answer this question using the transcript below. Keep answers to 1 sentence. (Attempt {attempt+1}/3)\n\nQuestion:\n{q}\n\nTranscript:\n{transcript_str}"
        ans = call_llm(prompt).strip()
        candidates.append(ans)
    
    synth_prompt = (
        f"Given the question and 3 candidate answers generated from a transcript, synthesize or select the single most accurate, complete, and concise 1-sentence Ground Truth answer.\n\n"
        f"Question:\n{q}\n\n"
        f"Candidate 1: {candidates[0]}\n"
        f"Candidate 2: {candidates[1]}\n"
        f"Candidate 3: {candidates[2]}\n\n"
        f"Output ONLY the final 1-sentence Ground Truth answer."
    )
    final_answer = call_llm(synth_prompt).strip()
    print(f"Ground Truth: {final_answer}")
