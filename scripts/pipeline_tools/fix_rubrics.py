import os
import json
import re

count = 0
for file in os.listdir("data/sharegpt/inputs_100"):
    if file.endswith("_rubric.json"):
        path = os.path.join("data/sharegpt/inputs_100", file)
        with open(path, "r") as f:
            content = f.read()
        
        # If it's already valid JSON, skip
        try:
            json.loads(content)
            continue
        except:
            pass
            
        # Try to extract JSON from markdown or raw text
        match = re.search(r'\[\s*\{.*?\}\s*\]', content, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
                with open(path, "w") as f:
                    json.dump(parsed, f, indent=2)
                count += 1
            except:
                pass
print(f"Salvaged {count} broken rubric files.")
