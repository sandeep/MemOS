import os
import re

# Patch generate_rubric.py
with open("src/generate_rubric.py", "r") as f:
    rubric_code = f.read()
    
if "rubric.raw.txt" not in rubric_code:
    rubric_code = rubric_code.replace(
        "response = call_llm(prompt)",
        "response = call_llm(prompt)\n    with open(transcript_path.replace('.json', '_rubric.raw.txt'), 'w') as f:\n        f.write(response)"
    )
    with open("src/generate_rubric.py", "w") as f:
        f.write(rubric_code)

# Patch extractor_recursive.py
with open("src/extractor_recursive.py", "r") as f:
    ext_code = f.read()

if "raw.txt" not in ext_code:
    ext_code = ext_code.replace(
        "raw_extraction = call_llm(sub_prompt)",
        "raw_extraction = call_llm(sub_prompt)\n        with open(output_file + '.raw.txt', 'w') as f:\n            f.write(raw_extraction)"
    )
    with open("src/extractor_recursive.py", "w") as f:
        f.write(ext_code)

print("Patched scripts with explicit raw output dumping.")
