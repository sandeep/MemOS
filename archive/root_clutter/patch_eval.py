import re

with open("src/evaluator.py", "r") as f:
    code = f.read()

# Add os import
code = code.replace("import sys\nimport re", "import os\nimport sys\nimport re")

new_generate = """def generate_answer_key(transcript_str: str) -> list:
    key_file = "answer_key.json"
    if os.path.exists(key_file):
        print(f"\\n--- PHASE 1: LOADING CACHED ANSWER KEY ({key_file}) ---")
        sys.stdout.flush()
        with open(key_file, 'r') as f:
            return json.load(f)

    print("\\n--- PHASE 1: GENERATING ANSWER KEY ---")
    sys.stdout.flush()
    answer_key = []
    for i, q in enumerate(QUESTIONS):
        candidates = []
        for attempt in range(3):
            print(f"Generating Ground Truth for Q{i+1} (sample {attempt+1}/3)...")
            sys.stdout.flush()
            prompt = f"Answer this question using the transcript below. Keep answers to 1 sentence. (Attempt {attempt+1}/3)\\n\\nQuestion:\\n{q}\\n\\nTranscript:\\n{transcript_str}"
            answer = call_llm(prompt).strip()
            candidates.append(answer)

        print(f"Synthesizing final Ground Truth for Q{i+1} from 3 samples...")
        sys.stdout.flush()
        synth_prompt = (
            f"Given the question and 3 candidate answers generated from a transcript, synthesize or select the single most accurate, complete, and concise 1-sentence Ground Truth answer.\\n\\n"
            f"Question:\\n{q}\\n\\n"
            f"Candidate 1: {candidates[0]}\\n"
            f"Candidate 2: {candidates[1]}\\n"
            f"Candidate 3: {candidates[2]}\\n\\n"
            f"Output ONLY the final 1-sentence Ground Truth answer."
        )
        final_answer = call_llm(synth_prompt).strip()
        if not final_answer and any(candidates):
            final_answer = next(c for c in candidates if c)
        answer_key.append(final_answer)
        
    with open(key_file, 'w') as f:
        json.dump(answer_key, f, indent=2)
        
    return answer_key"""

code = re.sub(r'def generate_answer_key\(transcript_str: str\) -> list:.*?return answer_key', new_generate, code, flags=re.DOTALL)

with open("src/evaluator.py", "w") as f:
    f.write(code)
print("Patched src/evaluator.py")
