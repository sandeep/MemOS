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
        backend_kwargs={"model_name": "nvidia/nemotron-3.5-lightning-30b-a3b", "sampling_args": {"temperature": 0.0}, "timeout": 180.0},
        environment="local",
        environment_kwargs={"context_payload": safe_transcript},
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
        
        CRITICAL REQUIREMENT:
        You must write your script to aggressively save the in-progress JSON state to 'output_rlms.json' after EVERY SINGLE CHUNK you process. Do NOT hold the entire state in memory and wait until the end. This provides interim updates and prevents data loss if the API times out mid-extraction.
        
        Make sure your python code executes quickly (under 30 seconds)."""
        
    import re
    # Ensure RLM writes to output_file instead of hardcoded
    base_prompt = re.sub(r"output[a-zA-Z0-9_]*\.json", output_file, base_prompt)

    # BUGFIX: We cannot inject {safe_transcript} directly into the prompt because a 77k-character string 
    # overwhelms the LLM and causes it to forget the system instructions. Instead, we instruct the 
    # agent to read the scrubbed JSON file from disk. We use abspath because the REPL runs in a sandbox.
    # BUGFIX 2: Actually, reading files from the sandbox is brittle. We now inject the transcript directly
    # into the sandbox via `context_payload`. The RLM library natively binds this to the variable `context`.
    prompt = f"{base_prompt}\n\nThe raw conversation transcript has been pre-loaded into your Python environment as a string variable named `context`.\nWrite your python script to chunk the `context` variable, process the chunks using `llm_query()`, and extract the Knowledge Graph."
    
    print("Running RLM completion...")
    try:
        response = rlm.completion(prompt)
    except Exception as e:
        raise RuntimeError(f"RLM Execution Failed: {e}") from e
    print("RLM Execution complete.")

    if (not os.path.exists(output_file) or os.path.getsize(output_file) == 0) and response:
        print(f"Agent did not create {output_file} (or it was empty). Attempting LLM JSON repair fallback...")
        if os.path.dirname(output_file):
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
        raw_text = response.response if hasattr(response, 'response') else str(response)
        
        # Decide which schema format to ask for based on the output filename
        if "v2" in output_file.lower():
            schema_hint = '{"Semantic": [{"subject": "...", "relation": "...", "object": "..."}], "Episodic": [{"step": 1, "subject": "...", "relation": "...", "object": "..."}], "Procedural": [], "Active": []}'
        else:
            schema_hint = '{"semantic_memory": {"nodes": [{"description": "..."}], "edges": [{"source": "...", "target": "...", "relation": "..."}]}, "episodic_ledger": {"events": [{"event": "...", "description": "..."}], "decisions": [], "rejected_branches": []}, "procedural_memory": {"instructions": [{"step": 1, "action": "..."}]}, "active_state": {"current_goal": "", "blockers": [], "next_action": ""}}'
            
        repair_prompt = (
            f"You are a strict data formatter. Convert the following text into a valid JSON object matching this schema exactly:\n"
            f"{schema_hint}\n\n"
            f"Output ONLY valid JSON. Do not use single quotes for keys, use double quotes. No markdown formatting.\n\n"
            f"Text to convert:\n{raw_text}"
        )
        
        from src.llm_utils import call_llm
        try:
            repaired_json = call_llm(repair_prompt, temp=0.1)
            # Basic cleanup if the LLM still wrapped it
            if repaired_json.startswith("```json"): repaired_json = repaired_json[7:]
            if repaired_json.startswith("```"): repaired_json = repaired_json[3:]
            if repaired_json.endswith("```"): repaired_json = repaired_json[:-3]
            repaired_json = repaired_json.strip()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(repaired_json)
            print(f"Repaired JSON saved to {output_file}")
            return True
        except Exception as e:
            print(f"Fallback repair failed: {e}. Writing raw text.")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(raw_text)

    print(f"Primary agent successfully extracted to {output_file}")
    return False

if __name__ == "__main__":
    if len(sys.argv) > 3:
        extract(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) > 2:
        extract(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1:
        extract(sys.argv[1])
    else:
        print("Usage: python src/extractor_rlms.py <transcript.json> [prompt.txt] [output.json]")
