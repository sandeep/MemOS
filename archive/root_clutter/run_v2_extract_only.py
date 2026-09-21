import json
from src.llm_utils import call_llm

with open("specs/test-case-conversation.json", "r") as f:
    transcript = json.dumps(json.load(f))[:5000]

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

Output ONLY valid JSON. No markdown formatting. Start immediately with {{.
"""
print("Extracting V2 Graph...")
v2_json_str = call_llm(prompt).strip()
print("\n--- RAW LLM OUTPUT ---")
print(v2_json_str)
