import json
import requests
import io
import sys
import contextlib
import multiprocessing
import os
import time
import re

NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

def call_llm(prompt: str) -> str:
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
    for attempt in range(5):
        try:
            response = requests.post(NVIDIA_URL, headers=headers, json=payload)
            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"].strip()
            
            with open("llm_calls.log", "a") as f:
                f.write(f"========== ATTEMPT {attempt+1} PROMPT ==========\n{prompt}\n")
                f.write(f"========== RAW RESPONSE ==========\n{text}\n\n")

            if "Here's a thinking process:" in text:
                parts = text.split("Here's a thinking process:")
                if len(parts) > 1:
                    pass
            return text
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                time.sleep(5 * (attempt + 1))
            else:
                return ""
        except Exception as e:
            return ""
    return ""

def _run_exec(code, globals_dict, output_queue):
    try:
        exec(code, globals_dict)
    except Exception as e:
        print(f"REPL Error: {e}")
    output_queue.put("Execution finished.")

def extract_with_repl(conversation_file: str, prompt_file: str):
    with open(conversation_file, 'r') as f:
        data = json.load(f)
    transcript = json.dumps(data)
    
    with open(prompt_file, 'r') as f:
        system_prompt = f.read()
    
    print(f"Initializing True RLM with Python REPL using prompt: {prompt_file}...")
    sandbox_globals = {"transcript": transcript, "llm_query": call_llm}
    
    llm_output = call_llm(system_prompt)
    import re
    matches = re.findall(r'```python(.*?)```', llm_output, re.DOTALL)
    if not matches:
        # Fallback: check if it started but didn't finish
        matches_unclosed = re.findall(r'```python(.*)', llm_output, re.DOTALL)
        if matches_unclosed:
            code_to_execute = matches_unclosed[0].strip()
            print("WARNING: Code block was not closed. Attempting to execute anyway...")
        else:
            print("No Python code generated.")
            return
    else:
        code_to_execute = matches[0].strip()
    print("RLM Generated Code:\n" + "="*40 + f"\n{code_to_execute}\n" + "="*40)
    
    # Run with 3600-second timeout
    print("Executing in REPL sandbox (3600s timeout)...")
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=_run_exec, args=(code_to_execute, sandbox_globals, queue))
    p.start()
    p.join(3600)
    
    if p.is_alive():
        print("REPL Execution TIMED OUT after 3600 seconds. Killing process.")
        p.terminate()
        p.join()
    else:
        print("REPL Output:\n" + queue.get())

if __name__ == "__main__":
    if len(sys.argv) > 2:
        extract_with_repl(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python src/rlm_repl_extractor.py <transcript.json> <prompt.txt>")
