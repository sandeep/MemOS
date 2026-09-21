import re

with open("run_pipeline.py", "r") as f:
    content = f.read()

# Replace the evaluate_pipeline section to add try/except
old_eval = """        results = evaluate_pipeline(os.path.join(original_cwd, scrubbed), valid_kgs)
        logger.record_scores(results)
        
        # 3. Write leaderboard
        with open(os.path.basename(leaderboard), "w") as f:
            f.write(f"# Leaderboard for {base_name} ({tag})\\n\\n")
            for k, v in results.items():
                f.write(f"- {k}: {v}%\\n")"""

new_eval = """        try:
            results = evaluate_pipeline(os.path.join(original_cwd, scrubbed), valid_kgs)
            logger.record_scores(results)
            
            # 3. Write leaderboard
            with open(os.path.basename(leaderboard), "w") as f:
                f.write(f"# Leaderboard for {base_name} ({tag})\\n\\n")
                for k, v in results.items():
                    f.write(f"- {k}: {v}%\\n")
        except Exception as e:
            logger.record_eval_error(str(e))
            print(f"Evaluation crashed: {e}")"""

content = content.replace(old_eval, new_eval)

# Wrap everything in try...finally logger.flush
old_func_start = """    # 1. Extract
    extractions = ["""

new_func_start = """    try:
        # 1. Extract
        extractions = ["""

content = content.replace(old_func_start, new_func_start)

# Indent everything between old_func_start and logger.flush
import textwrap

lines = content.split('\n')
start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if line.startswith("    try:"):
        if "extractions =" in lines[i+2]: # Make sure it's the right try block
            start_idx = i + 1
    if line.startswith("    logger.flush(log_file)"):
        end_idx = i

if start_idx != -1 and end_idx != -1:
    for i in range(start_idx, end_idx):
        lines[i] = "    " + lines[i]

    # Replace logger.flush with finally block
    lines[end_idx] = """    finally:
        logger.flush(log_file)"""

content = '\n'.join(lines)

with open("run_pipeline.py", "w") as f:
    f.write(content)
