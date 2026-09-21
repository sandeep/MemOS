import re

with open("run_pipeline.py", "r") as f:
    content = f.read()

# Add the extraction logic for Naive V2 and RLMS V2
content = content.replace(
    '("kg_v3_temporal", os.path.join(eval_dir, f"kg_v3_temporal_{tag}.json"), lambda: extract(scrubbed, "src/prompts/propositional_v3_temporal.txt", os.path.join(eval_dir, f"kg_v3_temporal_{tag}.json")))',
    '("kg_v3_temporal", os.path.join(eval_dir, f"kg_v3_temporal_{tag}.json"), lambda: extract(scrubbed, "src/prompts/propositional_v3_temporal.txt", os.path.join(eval_dir, f"kg_v3_temporal_{tag}.json"))),\n            ("kg_naive_v2", os.path.join(eval_dir, f"kg_naive_v2_{tag}.json"), lambda: extract(scrubbed, "src/prompts/naive_v2.txt", os.path.join(eval_dir, f"kg_naive_v2_{tag}.json"))),\n            ("kg_rlms_v2", os.path.join(eval_dir, f"kg_rlms_v2_{tag}.json"), lambda: extract(scrubbed, "src/prompts/rlms_v2.txt", os.path.join(eval_dir, f"kg_rlms_v2_{tag}.json")))'
)

# Add to valid_kgs loop
content = content.replace(
    'for kg in [kg_naive, kg_rlms, kg_prop, kg_prop_v2, kg_v3]:',
    'kg_naive_v2 = os.path.join(eval_dir, f"kg_naive_v2_{tag}.json")\n            kg_rlms_v2 = os.path.join(eval_dir, f"kg_rlms_v2_{tag}.json")\n            for kg in [kg_naive, kg_rlms, kg_prop, kg_prop_v2, kg_v3, kg_naive_v2, kg_rlms_v2]:'
)

with open("run_pipeline.py", "w") as f:
    f.write(content)

print("Patched run_pipeline.py with Naive V2 and RLMS V2.")
