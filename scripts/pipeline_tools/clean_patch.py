import re

with open("run_pipeline.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if '("kg_prop_v2", kg_prop_v2' in line:
        new_lines.append(line.rstrip() + ',\n')
        new_lines.append('            ("kg_v3_temporal", os.path.join(eval_dir, f"kg_v3_temporal_{tag}.json"), lambda: extract(scrubbed, "src/prompts/propositional_v3_temporal.txt", os.path.join(eval_dir, f"kg_v3_temporal_{tag}.json")))\n')
    elif 'for kg in [kg_naive, kg_rlms, kg_prop, kg_prop_v2]:' in line:
        new_lines.append('            kg_v3 = os.path.join(eval_dir, f"kg_v3_temporal_{tag}.json")\n')
        new_lines.append('            for kg in [kg_naive, kg_rlms, kg_prop, kg_prop_v2, kg_v3]:\n')
    else:
        new_lines.append(line)

with open("run_pipeline.py", "w") as f:
    f.writelines(new_lines)
