import sys
import json
from llm_utils import call_llm

def generate_rubric(transcript_path: str):
    with open(transcript_path, 'r') as f:
        transcript_str = json.dumps(json.load(f))
        
    prompt = f"""
You are an expert evaluator. Read the following conversational transcript and generate exactly 15 evaluation questions to test an AI's ability to extract knowledge from it. 

You must generate exactly 3 questions for each of the following 5 cognitive domains:
1. CONTROL: Verbatim extraction (exact quotes, titles, identifiers).
2. SEMANTIC: Abstract comprehension (core conflicts, definitions, beliefs).
3. EPISODIC: Temporal logic (sequence of events, chronological shifts).
4. PROCEDURAL: System mapping (step-by-step rules, frameworks proposed).
5. ACTIVE: Context awareness (unresolved tensions, immediate next steps, goals).

Output the result as a valid JSON array of 15 strings, e.g.:
[
  "(Control) What exact string...",
  "(Control) What title...",
  ...
]

Transcript:
{transcript_str}
"""
    print("Mechanically generating 15-question rubric...")
    response = call_llm(prompt)
    
    # Extract JSON array
    import re
    match = re.search(r'\[.*\]', response, re.DOTALL)
    if match:
        questions = json.loads(match.group(0))
        output_file = transcript_path.replace(".json", "_rubric.json")
        with open(output_file, 'w') as f:
            json.dump(questions, f, indent=2)
        print(f"Successfully generated {len(questions)} questions. Saved to {output_file}")
    else:
        print("Failed to parse JSON array from LLM response.")
        print(response)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/generate_rubric.py <transcript_path.json>")
        sys.exit(1)
    generate_rubric(sys.argv[1])
