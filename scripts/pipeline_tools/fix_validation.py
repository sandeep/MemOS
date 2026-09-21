import re

with open("run_pipeline.py", "r") as f:
    content = f.read()

content = content.replace(
    "if kg == kg_naive:",
    "if kg in [kg_naive, kg_naive_v2]:"
)

content = content.replace(
    'schema = "propositional_v2" if kg == kg_prop_v2 else "standard"',
    'schema = "propositional_v2" if kg in [kg_prop_v2, kg_v3] else "standard"'
)

with open("run_pipeline.py", "w") as f:
    f.write(content)
