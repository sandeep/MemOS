import json
from src.llm_utils import call_llm
from src.evaluator import QUESTIONS

ground_truth = [
    "The exact string the user uses for their personality type and cognitive style is entj and highly logical and crisp.",
    "The user expresses a fundamental conflict between their ingrained need for objective, quantifiable criteria and the subjective, experience-driven nature of taste-based professions, which lack verifiable standards but operate through sensory acuity, pattern recognition, and intersubjective agreements.",
    "The AI first defines the user's logical executive persona, then maps their engineering-driven need for objective criteria, diagnoses taste's lack of verifiable metrics, reframes taste as a specialized data processing system using sensory acuity and pattern recognition, elaborates its logic through shared lexicons and intersubjective agreements, and finally positions it as a coherent, measurable information-evaluation framework aligned with quantifiable value.",
    "The AI's immediate focus is reframing 'taste' as a logical, data-driven system to align with the user's engineering mindset and need for objective, measurable criteria."
]

def evaluate(kg_file):
    try:
        with open(kg_file, 'r') as f:
            kg_str = json.dumps(json.load(f))
    except Exception as e:
        return 0
    
    scores = []
    for i, q in enumerate(QUESTIONS):
        print(f"Retrieving Q{i+1} for {kg_file}...")
        retr_prompt = f"Answer this question using ONLY the Knowledge Graph below. Keep answers to 1 sentence. If the info is missing, say 'MISSING'.\n\nQuestion:\n{q}\n\nKnowledge Graph:\n{kg_str}"
        try:
            retr_ans = call_llm(retr_prompt).strip()
        except:
            retr_ans = "MISSING"
        
        print(f"Judging Q{i+1} for {kg_file}...")
        judge_prompt = f"Compare the TRUE Answer to the Retrieved Answer. Did the Retrieved Answer miss any critical facts? Give a score out of 100 as a SINGLE INTEGER ONLY on the first line.\n\nTRUE Answer:\n{ground_truth[i]}\n\nRetrieved Answer:\n{retr_ans}"
        try:
            resp = call_llm(judge_prompt).strip()
            score_line = resp.splitlines()[0]
            import re
            m = re.search(r'\b(100|\d{1,2})\b', score_line)
            score = int(m.group()) if m else 0
        except:
            score = 0
        scores.append(score)
        print(f"Score for Q{i+1}: {score}")
    
    return sum(scores)/len(scores) if scores else 0

files = ["output.json", "output_rlms.json", "output_propositional.json", "output_propositional_kg.json"]
for f in files:
    print(f"\n--- Evaluating {f} ---")
    final_score = evaluate(f)
    print(f"Final Score for {f}: {final_score}%")
