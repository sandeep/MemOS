import os
import re

# 1. Refactor llm_utils.py
with open("src/llm_utils.py", "r") as f:
    content = f.read()

if "task_id: str = None" not in content:
    content = content.replace(
        'def call_llm(prompt: str, model: str = "nvidia/nemotron-3.5-lightning-30b-a3b", temp: float = 0.0, max_tokens: int = 4096, cache_dir: str = "llm_cache") -> str:',
        'def call_llm(prompt: str, model: str = "nvidia/nemotron-3.5-lightning-30b-a3b", temp: float = 0.0, max_tokens: int = 4096, cache_dir: str = "llm_cache", task_id: str = None) -> str:'
    )

hash_logic = """    # Caching logic
    prompt_hash = hashlib.md5((prompt + model + str(temp)).encode()).hexdigest()
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{prompt_hash}.txt")"""

new_logic = """    # Caching logic
    os.makedirs(cache_dir, exist_ok=True)
    if task_id:
        cache_file = os.path.join(cache_dir, f"{task_id}.txt")
    else:
        prompt_hash = hashlib.md5((prompt + model + str(temp)).encode()).hexdigest()
        cache_file = os.path.join(cache_dir, f"{prompt_hash}.txt")"""

if "if task_id:" not in content:
    content = content.replace(hash_logic, new_logic)

with open("src/llm_utils.py", "w") as f:
    f.write(content)

# 2. Patch generate_rubric.py
with open("src/generate_rubric.py", "r") as f:
    rubric_content = f.read()
    
if "task_id=" not in rubric_content:
    rubric_content = rubric_content.replace(
        "response = call_llm(prompt)",
        'task_id = os.path.basename(transcript_path).replace(".json", "") + "_rubric"\n    response = call_llm(prompt, task_id=task_id)'
    )
rubric_content = re.sub(
    r'    with open\(transcript_path\.replace\(\'\.json\', \'_rubric\.raw\.txt\'\), \'w\'\) as f:\n        f\.write\(response\)\n',
    '',
    rubric_content
)
with open("src/generate_rubric.py", "w") as f:
    f.write(rubric_content)

# 3. Patch extractor_recursive.py
with open("src/extractor_recursive.py", "r") as f:
    ext_content = f.read()

if "task_id=" not in ext_content:
    ext_content = ext_content.replace(
        "raw_extraction = call_llm(sub_prompt)",
        'task_id = f"{os.path.basename(output_file).replace(\'.json\', \'\')}_chunk{i}"\n        raw_extraction = call_llm(sub_prompt, task_id=task_id)'
    )
ext_content = re.sub(
    r'        with open\(output_file \+ \'\.raw\.txt\', \'w\'\) as f:\n            f\.write\(raw_extraction\)\n',
    '',
    ext_content
)
with open("src/extractor_recursive.py", "w") as f:
    f.write(ext_content)

print("Cache refactoring successful!")
