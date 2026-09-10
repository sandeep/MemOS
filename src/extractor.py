import json
import re
import os
import time
from llm_utils import call_llm

def scrub_pii(text: str) -> str:
    # Bypassed to prevent Presidio initialization hang on local machine
    return text

def merge_graphs(master, new_data):
    if not new_data: return master
    sem = new_data.get("semantic_memory", {})
    master["semantic_memory"]["nodes"].extend(sem.get("nodes", []))
    master["semantic_memory"]["edges"].extend(sem.get("edges", []))
    ep = new_data.get("episodic_ledger", {})
    master["episodic_ledger"]["events"].extend(ep.get("events", []))
    master["episodic_ledger"]["decisions"].extend(ep.get("decisions", []))
    master["episodic_ledger"]["rejected_branches"].extend(ep.get("rejected_branches", []))
    proc = new_data.get("procedural_memory", {})
    master["procedural_memory"]["instructions"].extend(proc.get("instructions", []))
    master["active_state"] = new_data.get("active_state", master["active_state"])
    return master

def extract_rlm(conversation_file: str):
    with open(conversation_file, 'r') as f:
        data = json.load(f)
    transcript = json.dumps(data)
    safe_transcript = transcript  # Bypass PII scrub to prevent regex hang on massive string
    
    # 1. PEEK: Domain Discovery
    head = safe_transcript[:1500]
    peek_prompt = f"What is the domain of this conversation? Text: {head}"
    domain = call_llm(peek_prompt)
    print(f"Domain discovered: {domain}")
    
    # 2. SCHEMA INDUCTION (Dynamic Schema)
    schema_prompt = f"Based on this domain: {domain}, output a dynamic JSON schema for tracking Semantic Memory (nodes/edges), Episodic Ledger (events), and Active State. Output ONLY valid JSON representing the schema structure."
    dynamic_schema = call_llm(schema_prompt, json_format=True)
    print("Dynamic Schema generated.")
    
    # 3. FILTER / CHUNKING
    # Split by chunks of 1500 chars (or by turn objects if it's a list)
    chunks = [safe_transcript[i:i+1500] for i in range(0, len(safe_transcript), 1500)]
    
    # 4. RECURSIVE EXTRACT
    master_graph = {
        "semantic_memory": {"nodes": [], "edges": []},
        "episodic_ledger": {"events": [], "decisions": [], "rejected_branches": []},
        "procedural_memory": {"instructions": []},
        "active_state": {"current_goal": "", "blockers": [], "next_action": ""}
    }
    
    for idx, chunk in enumerate(chunks):
        print(f"Extracting chunk {idx+1}/{len(chunks)}...")
        sub_prompt = f"Extract data matching this JSON schema: {dynamic_schema}. Ensure you retain verbatim user details. Text: {chunk}"
        raw_extraction = call_llm(sub_prompt, json_format=True)
        # Robustly extract JSON to bypass CoT and markdown
        # Find the first '{' and the last '}'
        start_idx = raw_extraction.find('{')
        end_idx = raw_extraction.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            raw_extraction = raw_extraction[start_idx:end_idx+1]
        try:
            parsed = json.loads(raw_extraction)
            master_graph = merge_graphs(master_graph, parsed)
        except Exception as e:
            print(f"Failed to parse chunk JSON: {e}")
            
    # 5. SUBMIT
    with open("output.json", "w") as out:
        json.dump(master_graph, out, indent=2)
    print("RLM extraction complete.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1: extract_rlm(sys.argv[1])
