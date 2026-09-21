import re

file_path = "docs/superpowers/specs/2026-09-12-test-case-scaffolding-design.md"
with open(file_path, "r") as f:
    code = f.read()

# Fix directory diagram
old_tree = """              ├── answer_key.json         <-- Generated Ground Truth
              ├── output_rlms.json        <-- Extractor A output
              └── output_propositional.json<- Extractor B output"""
new_tree = """              ├── answer_key.json         <-- Generated Ground Truth
              ├── kg_naive.json           <-- Naive baseline output
              ├── kg_rlms.json            <-- Standard RLM output
              └── kg_propositional.json   <-- Propositional hybrid output"""
code = code.replace(old_tree, new_tree)

# Fix Extraction Phase text
old_text = "The script automatically runs both the baseline RLM extractor and the Propositional KG extractor using the scrubbed input. It writes their outputs into the `working/evaluations/[name]/` directory."
new_text = "The script automatically runs all three extractors (Naive, RLM, and Propositional) using the scrubbed input. It enforces consistent naming for the outputs (`kg_naive.json`, `kg_rlms.json`, `kg_propositional.json`) and writes them into the `working/evaluations/[name]/` directory."
code = code.replace(old_text, new_text)

# Fix Evaluation Phase text
old_eval = "Tests both extracted KGs against the answer key."
new_eval = "Tests all three extracted KGs against the answer key."
code = code.replace(old_eval, new_eval)

with open(file_path, "w") as f:
    f.write(code)
print("Patched spec.")
