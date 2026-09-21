import re
import json

def extract_json(log_path, output_path):
    with open(log_path, 'r') as f:
        content = f.read()
    
    if "Final Answer" in content:
        block = content.split("Final Answer")[1].split("RLM Execution")[0]
        # Remove all drawing characters and leading/trailing whitespace
        clean_block = re.sub(r'[│╭╰─╮╯═★]', '', block).strip()
        # Join lines that were broken by the box drawing formatting
        # This is tricky because string literals might have been wrapped.
        # Let's just remove newlines that don't follow a valid JSON character
        clean_block = clean_block.replace('\n', '')
        # We need to format it properly. Let's find the first [ or {
        match = re.search(r'([\[\{].*[\]\}])', clean_block)
        if match:
            clean_block = match.group(1)
            
        try:
            data = json.loads(clean_block)
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Success for {output_path}")
        except Exception as e:
            print("Failed to decode:", e)

extract_json('prop_only.log', 'output_propositional.json')
extract_json('prop_kg.log', 'output_propositional_kg.json')
