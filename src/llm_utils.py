import os
import time
import requests
import hashlib

NVIDIA_URL = "https://openrouter.ai/api/v1/chat/completions"

def call_llm(prompt: str, model: str = "meta-llama/llama-3.1-70b-instruct", temp: float = 0.0, max_tokens: int = 4096, cache_dir: str = "llm_cache", task_id: str = None) -> str:
    """
    Unified LLM calling function that handles:
    1. Caching
    2. Rate-limit retries
    3. Stripping 'Thinking Process' logs from reasoning models
    """
    # Caching logic
    os.makedirs(cache_dir, exist_ok=True)
    if task_id:
        cache_file = os.path.join(cache_dir, f"{task_id}.txt")
    else:
        prompt_hash = hashlib.md5((prompt + model + str(temp)).encode()).hexdigest()
        cache_file = os.path.join(cache_dir, f"{prompt_hash}.txt")
    
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            return f.read()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set.")
        return ""
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temp,
        "max_tokens": max_tokens
    }
    
    for attempt in range(5):
        try:
            response = requests.post(NVIDIA_URL, headers=headers, json=payload, timeout=180)
            response.raise_for_status()
            text = response.json()["choices"][0]["message"]["content"].strip()
            
            # ---------------------------------------------------------
            # THE SINGLE PLACE TO REMOVE THE "THINKING" LOGS
            # ---------------------------------------------------------
            if "Here's a thinking process:" in text:
                parts = text.split("Here's a thinking process:")
                if len(parts) > 1:
                    text = parts[-1]
                    # If there's a markdown block ending the thought process, strip it out
                    if "\n\n" in text:
                        text = "\n\n".join(text.split("\n\n")[1:])
            
            # Strip markdown json blocks if present
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            text = text.strip()
            
            # Save to cache
            with open(cache_file, "w") as f:
                f.write(text)
                
            return text
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                time.sleep(5 * (attempt + 1))
            elif response.status_code in [500, 502, 503, 504]:
                print(f"Server Error {response.status_code}, retrying...")
                time.sleep(5 * (attempt + 1))
            else:
                print(f"HTTP Error: {e}")
                raise RuntimeError(f"LLM API HTTP Error: {e}")
        except Exception as e:
            print(f"LLM Connection Error: {e}")
            time.sleep(2)
            
    raise RuntimeError("LLM Connection failed after 5 retries.")
