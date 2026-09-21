with open("src/generate_rubric.py", "r") as f:
    code = f.read()
    
if "re.sub" not in code:
    code = code.replace(
        "questions = json.loads(match.group(0))",
        "json_str = match.group(0)\n        json_str = re.sub(r'//.*', '', json_str)\n        questions = json.loads(json_str)"
    )
    with open("src/generate_rubric.py", "w") as f:
        f.write(code)
print("Patched rubric parser to strip JS comments.")
