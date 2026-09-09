import json
import requests
import re
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def scrub_pii(text: str) -> str:
    results = analyzer.analyze(text=text, language='en')
    return anonymizer.anonymize(text=text, analyzer_results=results).text

def call_llm(prompt: str, json_format: bool = False) -> str:
    payload = {"model": "gemma4", "prompt": prompt, "stream": False, "options": {"temperature": 0.0}}
    if json_format: payload["format"] = "json"
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        print(f"Error calling LLM: {e}")
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
