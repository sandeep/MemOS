with open("src/evaluator.py", "r") as f:
    eval_content = f.read()

if "task_id=" not in eval_content:
    eval_content = eval_content.replace(
        'ans = call_llm(prompt, model=llm_model, temp=0.0)',
        'task_id = f"eval_{os.path.basename(transcript_path)}_{i}_{attempt}"\n                ans = call_llm(prompt, model=llm_model, temp=0.0, task_id=task_id)'
    )
    with open("src/evaluator.py", "w") as f:
        f.write(eval_content)
print("Patched evaluator cache")
