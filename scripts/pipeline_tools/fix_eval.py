import json

with open('src/evaluator.py', 'r') as f:
    lines = f.readlines()

with open('src/evaluator.py', 'w') as f:
    for line in lines:
        if 'for i, q in enumerate(QUESTIONS):' in line:
            # We assume QUESTIONS is defined locally or we get it from the answer key
            f.write("    QUESTIONS = get_questions(transcript_path) if 'transcript_path' in locals() else [item['question'] for item in json.load(open(answer_key_path))]\n")
            f.write(line.replace('QUESTIONS', 'QUESTIONS'))
        else:
            f.write(line)
