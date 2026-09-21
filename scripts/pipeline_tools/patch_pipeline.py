with open("run_pipeline.py", "r") as f:
    content = f.read()
    
if "kg_v3_temporal" not in content:
    content = content.replace(
        "(\"kg_prop_v2\", kg_prop_v2, lambda: extract(scrubbed, \"src/prompts/propositional_v2_kg.txt\", kg_prop_v2))",
        "(\"kg_prop_v2\", kg_prop_v2, lambda: extract(scrubbed, \"src/prompts/propositional_v2_kg.txt\", kg_prop_v2)),\n            (\"kg_v3_temporal\", os.path.join(output_dir, f\"kg_v3_temporal_{ts}_{model}.json\"), lambda: extract(scrubbed, \"src/prompts/propositional_v3_temporal.txt\", os.path.join(output_dir, f\"kg_v3_temporal_{ts}_{model}.json\")))"
    )
    with open("run_pipeline.py", "w") as f:
        f.write(content)

print("Patched run_pipeline.py with V3.")
