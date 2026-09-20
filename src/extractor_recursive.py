import sys
import json
import os
import re
from src.llm_utils import call_llm
from src.extractor import scrub_pii, merge_graphs

def extract(conversation_file: str, prompt_file: str = None, output_file: str = "output_recursive.json"):
    # 1. Load and Scrub Transcript
    with open(conversation_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    safe_transcript = scrub_pii(json.dumps(data))
    
    # 2. Load Base Prompt
    if prompt_file and os.path.exists(prompt_file):
        with open(prompt_file, 'r', encoding='utf-8') as f:
            base_prompt = f.read()
            # Clean up the old misleading prompt instructions
            base_prompt = base_prompt.replace("The raw conversation transcript has been injected into your Python environment as a string variable named `context`.", "")
            base_prompt = base_prompt.replace("You have access to a Python REPL.", "")
            base_prompt = base_prompt.replace("You also have a function `llm_query(prompt: str) -> str` which you can use to prompt yourself or sub-agents on chunks of text.", "")
    else:
        base_prompt = (
            "You are a Knowledge Graph extraction system.\n"
            "Extract a 4-part JSON Knowledge Graph (Semantic, Episodic, Procedural, Active).\n"
            "Return ONLY a valid JSON object. Do not output any markdown formatting.\n"
            "Example Format: {\"semantic_memory\": {\"nodes\": [], \"edges\": []}, \"episodic_ledger\": {\"events\": [], \"decisions\": [], \"rejected_branches\": []}, \"procedural_memory\": {\"instructions\": []}, \"active_state\": {\"current_goal\": \"\", \"blockers\": [], \"next_action\": \"\"}}"
        )
        
    # 3. Chunk Transcript (3000 chars)
    chunk_size = 10000
    chunks = [safe_transcript[i:i+chunk_size] for i in range(0, len(safe_transcript), chunk_size)]
    
    master_graph = {}
    
    # 4. Iterate over chunks
    for idx, chunk in enumerate(chunks):
        print(f"[{output_file}] Extracting chunk {idx+1}/{len(chunks)}...")
        
        # Build prompt for this chunk, incorporating the running master graph state
        sub_prompt = (
            f"{base_prompt}\n\n"
            f"Here is the text chunk to process:\n\n{chunk}\n\n"
            f"Return ONLY the extracted JSON."
        )
        
        raw_extraction = call_llm(sub_prompt)
        
        # 5. Robustly parse JSON blocks
        json_blocks = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', raw_extraction, re.DOTALL)
        
        if not json_blocks:
            start_idx = raw_extraction.find('{')
            end_idx = raw_extraction.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                json_blocks = [raw_extraction[start_idx:end_idx+1]]
                
        for block in json_blocks:
            try:
                parsed = json.loads(block)
                master_graph = merge_graphs(master_graph, parsed)
            except Exception as e:
                print(f"[{output_file}] Failed to parse chunk JSON block: {e}")
                
    # 6. Save final output
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(master_graph, f, indent=2)
        
    print(f"Primary agent successfully extracted to {output_file}")
    
    # Return false to match previous signature (repaired = False)
    return False

if __name__ == "__main__":
    if len(sys.argv) > 3:
        extract(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) > 2:
        extract(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1:
        extract(sys.argv[1])
    else:
        print("Usage: python src/extractor_recursive.py <transcript.json> [prompt.txt] [output.json]")
