import re

file_path = "docs/superpowers/plans/2026-09-12-test-case-scaffolding.md"
with open(file_path, "r") as f:
    code = f.read()

# Update answer_key naming
code = code.replace(
    'answer_key.json gets saved correctly',
    'answer_key gets saved with the date and model tag'
)
code = code.replace(
    'answer_key.json',
    'answer_key_{tag}.json'
)

# Update reconstitution task note
code += """\n### Task 5: Reconstitution Symlinks (Architecture Setup)\n
- [ ] **Step 1: Define symlink behavior for Reconstituted KGs**
We will ensure that when the Reconstitutor generates `kg_propositional_DATE_MODEL_reconstituted.json`, it also creates/updates a `latest.json` symlink pointing to it, so downstream systems always know where to look.
"""

with open(file_path, "w") as f:
    f.write(code)
print("Patched plan.")
