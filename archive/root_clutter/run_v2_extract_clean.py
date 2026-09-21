import json
from src.llm_utils import call_llm

# Extract clean text from the JSON structure
with open("specs/test-case-conversation.json", "r") as f:
    data = json.load(f)

# Extract only the user/assistant messages, ignoring all the JSON overhead
transcript_text = ""
for item in data:
    for msg in item.get('history', []):
        role = msg.get('role', 'unknown')
        for part in msg.get('parts', []):
            transcript_text += f"{role.upper()}: {part.get('text', '')}\n"

# Only grab the first 10000 chars of actual conversational text to stay within context windows
transcript_clean = transcript_text[:10000]

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
{transcript_clean}

Output ONLY valid JSON wrapped in ```json ... ```. No reasoning!
"""
print("Extracting V2 Graph with CLEAN text...")
v2_json_str = call_llm(prompt).strip()
print("\n--- RAW LLM OUTPUT ---")
print(v2_json_str)
