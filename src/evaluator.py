"""
evaluator.py
3-Stage Evaluator: (1) Answer Key (2) Retriever (3) Judge
Scores multiple KG files against a raw transcript.
"""
import json
import sys
import re
import os
from llm_utils import call_llm


import json
import os
import sys

def get_questions(transcript_path):
    rubric_path = transcript_path.replace(".json", "_rubric.json")
    if os.path.exists(rubric_path):
        with open(rubric_path, 'r') as f:
            data = json.load(f)
            questions = []
            for item in data:
                if isinstance(item, dict) and "question" in item:
                    questions.append(f"({item.get('domain', 'Domain')}) {item['question']}")
                elif isinstance(item, str):
                    questions.append(item)
            return questions
    return [
        "(Control) The user begins their message with a self-description that includes a specific personality identifier and two adjectives; what is the exact string the user uses for their personality type and cognitive style?",
        "(Control) What specific technology company or ecosystem is repeatedly used as the primary historical analogy for curating taste?",
        "(Control) What is the specific title or role of the user (e.g., SVP/CPO) mentioned in the conversation?",
        "(Semantic) What is the core conflict or objective vs subjective tension expressed by the user regarding taste-based professions?",
        "(Semantic) How does the AI define 'taste' functionally rather than aesthetically? What is its definition of taste as a system?",
        "(Semantic) According to the dialogue, what is the critical difference between 'intersubjective agreement' and 'objective truth'?",
        "(Episodic) What is the sequence of logical steps the AI takes to reframe 'taste' as a data processing system for the user?",
        "(Episodic) At what point in the conversation does the focus shift from philosophical definitions of taste to economic or systemic value creation?",
        "(Episodic) Describe the user's initial frustration or premise when the conversation started compared to where it ended.",
        "(Procedural) What are the specific, step-by-step mechanisms proposed to convert subjective quality into economic worth?",
        "(Procedural) What are the foundational rules or guidelines (like the 'Human Interface Guidelines' analogy) required to curate a taste-based platform?",
        "(Procedural) How is a developer or creator supposed to interact with the 'App Store of Taste' according to the proposed system?",
        "(Active) What is the immediate focus or unresolved question the AI is trying to address to bridge the gap for the user at the end of the text?",
        "(Active) What actionable goal or next step is the user attempting to achieve by dissecting the mechanics of taste?",
        "(Active) What remains the biggest blocker or unproven assumption in the AI's proposed system of taste?"
    ]

# The global QUESTIONS list will be initialized when run_pipeline is called.
QUESTIONS = get_questions("dummy")

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

def retrieve_answers(kg_str: str) -> list:
    retrieved = []
    for q in QUESTIONS:
        prompt = f"Answer this question using ONLY the Knowledge Graph below. Keep answers to 1 sentence. If the info is missing, say 'MISSING'.\n\nQuestion:\n{q}\n\nKnowledge Graph:\n{kg_str}"
        ans = call_llm(prompt).strip()
        retrieved.append(ans)
    return retrieved

def judge_answers(answer_key: list, retrieved: list) -> list:
    scores = []
    for base_ans, retr_ans in zip(answer_key, retrieved):
        prompt = f"Compare the TRUE Answer to the Retrieved Answer. Did the Retrieved Answer miss any critical facts? Give a score out of 100 as a SINGLE INTEGER ONLY on the first line, followed by a 1-sentence explanation on the next line.\n\nTRUE Answer:\n{base_ans}\n\nRetrieved Answer:\n{retr_ans}"
        resp = call_llm(prompt).strip()
        
        first_line = resp.splitlines()[0] if resp else ""
        try:
            cleaned = re.sub(r'^(?:Q\d+[:.]?|\d+[\.\)]|\bScore\b:?)\s*', '', first_line.strip(), flags=re.IGNORECASE)
            score_match = re.search(r'\b(100|\d{1,2})\b', cleaned) or re.search(r'\b(100|\d{1,2})\b', first_line)
            score = int(score_match.group()) if score_match else 0
        except (ValueError, AttributeError):
            score = 0
        scores.append(score)
    return scores

def run_pipeline(transcript_file: str, kg_files: list):
    global QUESTIONS
    QUESTIONS = get_questions(transcript_file)
    with open(transcript_file, 'r') as f:
        # BUGFIX: Previously sliced as [:8000]. The LLM Judge must evaluate against the FULL transcript.
        transcript_str = json.dumps(json.load(f))
        
    base_transcript = os.path.basename(transcript_file).replace(".json", "")
    answer_key_file = f"{base_transcript}_answer_key.json"
    
    if os.path.exists(answer_key_file) and os.path.getsize(answer_key_file) > 0:
        print(f"\n--- PHASE 1: LOADING ANSWER KEY (found {answer_key_file}) ---")
        with open(answer_key_file, "r") as f:
            answer_key = json.load(f)
    else:
        answer_key = generate_answer_key(transcript_str)
        # Save the answer key to disk for visibility
        with open(answer_key_file + ".tmp", "w") as f:
            json.dump(answer_key, f, indent=2)
        os.rename(answer_key_file + ".tmp", answer_key_file)
    
    results = {}
    for kg_file in kg_files:
        print(f"\n--- PHASE 2 & 3: EVALUATING {kg_file} ---")
        try:
            with open(kg_file, 'r') as f:
                kg_str = json.dumps(json.load(f))
        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            print(f"Error loading {kg_file}: {e}. Skipping.")
            continue
            
        base_name = os.path.basename(kg_file).replace(".json", "")
        retrieved_file = f"{base_name}_retrieved.json"
        
        if os.path.exists(retrieved_file) and os.path.getsize(retrieved_file) > 0:
            print(f"Loading retrieved answers from {retrieved_file}")
            with open(retrieved_file, "r") as f:
                retrieved = json.load(f)
        else:
            retrieved = retrieve_answers(kg_str)
            # Save retrieved answers to disk for visibility
            with open(retrieved_file + ".tmp", "w") as f:
                json.dump(retrieved, f, indent=2)
            os.rename(retrieved_file + ".tmp", retrieved_file)
            
        scores_file = f"{base_name}_scores.json"
        if os.path.exists(scores_file) and os.path.getsize(scores_file) > 0:
            print(f"Loading scores from {scores_file}")
            with open(scores_file, "r") as f:
                scores = json.load(f)
        else:
            scores = judge_answers(answer_key, retrieved)
            # Save scores to disk for visibility
            with open(scores_file + ".tmp", "w") as f:
                json.dump(scores, f, indent=2)
            os.rename(scores_file + ".tmp", scores_file)
        
        avg_score = sum(scores) / len(scores) if scores else 0
        results[kg_file] = avg_score
        print(f"Final Score for {kg_file}: {avg_score}%")
        
    print("\n======================================")
    print("FINAL LEADERBOARD:")
    for file, score in results.items():
        print(f"{file}: {score}%")
    print("======================================")
    return results

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 src/evaluator.py <transcript.json> <kg_file1.json> [kg_file2.json ...]")
        sys.exit(1)
    run_pipeline(sys.argv[1], sys.argv[2:])
