import json
import requests
import re
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

import os
import time

NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def scrub_pii(text: str) -> str:
    results = analyzer.analyze(text=text, language='en')
    return anonymizer.anonymize(text=text, analyzer_results=results).text

def call_llm(prompt: str, json_format: bool = False) -> str:
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        print("ERROR: NVIDIA_API_KEY not set.")
        return ""
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "nvidia/nemotron-3.5-lightning-30b-a3b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 4096
    }
    # Currently NVIDIA NIM doesn't support strict JSON format flag universally, 
    # but the prompt asks for JSON.
    for attempt in range(5):
        try:
            response = requests.post(NVIDIA_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"].strip()
            
            # Clean CoT just in case
            if "Here's a thinking process:" in text:
                parts = text.split("Here's a thinking process:")
                if len(parts) > 1:
                    pass # We will rely on json.loads downstream
            return text
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                time.sleep(5 * (attempt + 1))
            else:
                return ""
        except Exception as e:
            return ""
    return ""

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
    safe_transcript = scrub_pii(transcript)
    
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
        # Robustly extract JSON to bypass CoT
        match = re.search(r'\{.*\}', raw_extraction, re.DOTALL)
        if match:
            raw_extraction = match.group(0)
        try:
            parsed = json.loads(raw_extraction)
            master_graph = merge_graphs(master_graph, parsed)
        except:
            print("Failed to parse chunk JSON.")
            
    # 5. SUBMIT
    with open("output.json", "w") as out:
        json.dump(master_graph, out, indent=2)
    print("RLM extraction complete.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1: extract_rlm(sys.argv[1])
