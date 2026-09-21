import json
import re
from src.llm_utils import call_llm
from src.evaluator import generate_answer_key, retrieve_answers, judge_answers

# 1. Load transcript
with open("specs/test-case-conversation.json", "r") as f:
    transcript = json.dumps(json.load(f))[:5000]

# 2. Extract V2 Graph
prompt = f"""You are extracting a Knowledge Graph from a transcript.
Output a JSON object with 4 keys: Semantic, Episodic, Procedural, Active.
Inside each bucket, output a list of STRICT Triples.
A Triple MUST be a JSON object with EXACTLY 3 string keys: "subject", "relation", "object".
For the Episodic bucket only, include an integer "step" key to preserve narrative timeline.

Example:
{{
  "Semantic": [
    {{"subject": "User", "relation": "possesses_trait", "object": "ENTJ personality"}}
  ],
  "Episodic": [
    {{"step": 1, "subject": "User", "relation": "expressed_skepticism_about", "object": "unquantifiable metrics"}}
  ],
  "Procedural": [],
  "Active": []
}}

Transcript:
{transcript}

Output ONLY valid JSON wrapped in ```json ... ```. No reasoning!
"""
v2_json_str = call_llm(prompt).strip()
match = re.search(r'```json\s*(.*?)\s*```', v2_json_str, re.DOTALL)
if match:
    v2_json_str = match.group(1).strip()
else:
    match = re.search(r'\{.*\}', v2_json_str, re.DOTALL)
    if match:
        v2_json_str = match.group(0).strip()

with open("output_propositional_v2_kg.json", "w") as f:
    f.write(v2_json_str)

# 3. Evaluate
transcript_for_eval = transcript[:8000]
answer_key = generate_answer_key(transcript_for_eval)

with open("output_propositional_v2_kg.json", "r") as f:
    kg_str = f.read()

retrieved = retrieve_answers(kg_str)
scores = judge_answers(answer_key, retrieved)
avg_score = sum(scores) / len(scores) if scores else 0

for i, (retr, score) in enumerate(zip(retrieved, scores)):
    print(f"\nQ{i+1} Score: {score}")
    print(f"Retrieved: {retr}")

print(f"\nFINAL V2 SCORE: {avg_score}%")
