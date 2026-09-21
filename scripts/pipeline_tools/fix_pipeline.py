import re

with open("run_pipeline.py", "r") as f:
    content = f.read()

# Fix the extractions array
content = re.sub(
    r'\("kg_v3_temporal".*?\)',
    '("kg_v3_temporal", os.path.join(eval_dir, f"kg_v3_temporal_{tag}.json"), lambda: extract(scrubbed, "src/prompts/propositional_v3_temporal.txt", os.path.join(eval_dir, f"kg_v3_temporal_{tag}.json")))',
    content
)

# Add to valid_kgs loop
content = content.replace(
    "for kg in [kg_naive, kg_rlms, kg_prop, kg_prop_v2]:",
    "kg_v3 = os.path.join(eval_dir, f\"kg_v3_temporal_{tag}.json\")\n            for kg in [kg_naive, kg_rlms, kg_prop, kg_prop_v2, kg_v3]:"
)

with open("run_pipeline.py", "w") as f:
    f.write(content)

print("Fixed run_pipeline.py")
