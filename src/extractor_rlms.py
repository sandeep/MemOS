"""
extractor_rlms.py
Dynamic Recursive Language Model (RLM) pipeline that writes and executes its own parsing code.
"""
import os
import sys
import json
from rlm import RLM
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Set up NVIDIA's OpenAI-compatible endpoint
os.environ["OPENAI_API_KEY"] = os.environ.get("NVIDIA_API_KEY", "")
os.environ["OPENAI_BASE_URL"] = "https://integrate.api.nvidia.com/v1"

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def scrub_pii(text: str) -> str:
    results = analyzer.analyze(text=text, language='en')
    return anonymizer.anonymize(text=text, analyzer_results=results).text

def extract(conversation_file: str, prompt_file: str = None, output_file: str = "output_rlms.json"):
    with open(conversation_file, 'r') as f:
        data = json.load(f)
    
    # Scrub the raw text
    safe_transcript = scrub_pii(json.dumps(data))
    
    print("Initializing RLMs library with Gemma-4...")
    # The RLM will execute its own Python REPL under the hood
    rlm = RLM(
        backend="openai",
        backend_kwargs={"model_name": "google/gemma-4-31b-it", "sampling_args": {"temperature": 0.0}},
        verbose=True
    )
    
    if prompt_file and os.path.exists(prompt_file):
        with open(prompt_file, 'r') as f:
            base_prompt = f.read()
    else:
        # Fallback to the default 4-part KG prompt
        base_prompt = f"""You are a Knowledge Graph extraction system.
        I have provided the raw conversation transcript below.
        Your task is to write a python program to loop through this transcript and extract it into a 4-part JSON Knowledge Graph (Semantic, Episodic, Procedural, Active).
        
        Save the final output JSON to 'output_rlms.json'.
        Make sure your python code executes quickly (under 30 seconds)."""
        
    import re
    # Ensure RLM writes to output_file instead of hardcoded
    base_prompt = re.sub(r"output[a-zA-Z0-9_]*\.json", output_file, base_prompt)

    prompt = f"{base_prompt}\n\nTranscript:\n{safe_transcript[:5000]}"
    
    print("Running RLM completion...")
    response = rlm.completion(prompt)
    print("RLM Execution complete.")

    if (not os.path.exists(output_file) or os.path.getsize(output_file) == 0) and response:
        print(f"Agent did not create {output_file} (or it was empty). Saving raw stdout fallback...")
        if os.path.dirname(output_file):
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            try:
                f.write(response.choices[0].message.content)
            except Exception:
                f.write(str(response))

if __name__ == "__main__":
    if len(sys.argv) > 3:
        extract(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) > 2:
        extract(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1:
        extract(sys.argv[1])
    else:
        print("Usage: python src/extractor_rlms.py <transcript.json> [prompt.txt] [output.json]")
