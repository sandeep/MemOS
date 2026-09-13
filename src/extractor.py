import json
import re
"""
extractor.py
Naive static extraction pipeline that uses fixed-size chunking and JSON regex parsing.
"""

import os
import time
from llm_utils import call_llm
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()


def scrub_pii(text: str) -> str:
    print("Scrubbing PII from text before extraction...")
    results = analyzer.analyze(text=text, language='en')
    return anonymizer.anonymize(text=text, analyzer_results=results).text

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

def extract_rlm(conversation_file: str, output_file: str = "output.json"):
    with open(conversation_file, 'r') as f:
        data = json.load(f)
    transcript = json.dumps(data)
    safe_transcript = scrub_pii(transcript)
    
    # 3. FILTER / CHUNKING
    # Split by chunks of 3000 chars to match typical RLM chunk size
    chunks = [safe_transcript[i:i+3000] for i in range(0, len(safe_transcript), 3000)]
    
    # 4. RECURSIVE EXTRACT
    master_graph = {
        "semantic_memory": {"nodes": [], "edges": []},
        "episodic_ledger": {"events": [], "decisions": [], "rejected_branches": []},
        "procedural_memory": {"instructions": []},
        "active_state": {"current_goal": "", "blockers": [], "next_action": ""}
    }
    
    for idx, chunk in enumerate(chunks):
        print(f"Extracting chunk {idx+1}/{len(chunks)}...")
        sub_prompt = (
            f"Extract a 4-part knowledge graph from the following text. "
            f"Return ONLY a valid JSON object with these exact keys: 'semantic_memory', 'episodic_ledger', 'procedural_memory', and 'active_state'. "
            f"Do not output any markdown formatting, thinking, or conversational filler. Output ONLY raw JSON.\n\n"
            f"Text: {chunk}\n\n"
            f"Example Format: {{\"semantic_memory\": {{\"nodes\": [], \"edges\": []}}, \"episodic_ledger\": {{\"events\": [], \"decisions\": [], \"rejected_branches\": []}}, \"procedural_memory\": {{\"instructions\": []}}, \"active_state\": {{\"current_goal\": \"\", \"blockers\": [], \"next_action\": \"\"}}}}"
        )
        raw_extraction = call_llm(sub_prompt)
        
        # Robustly extract JSON to bypass CoT and markdown
        start_idx = raw_extraction.find('{')
        end_idx = raw_extraction.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
            raw_extraction = raw_extraction[start_idx:end_idx+1]
            
        try:
            parsed = json.loads(raw_extraction)
            master_graph = merge_graphs(master_graph, parsed)
        except Exception as e:
            print(f"Failed to parse chunk JSON: {e}")
            
    # 5. SUBMIT
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    with open(output_file, "w") as out:
        json.dump(master_graph, out, indent=2)
    print("Baseline extraction complete.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2: extract_rlm(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1: extract_rlm(sys.argv[1])
