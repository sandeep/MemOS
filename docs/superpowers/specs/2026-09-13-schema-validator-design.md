# Spec: Knowledge Graph Schema Validator

## 1. Goal
Introduce a "Fail Fast" validation gate between the Extraction phase and the Evaluation phase. This prevents malformed outputs (hallucinated schemas, missing keys, or plain text instead of JSON) from burning expensive API tokens in the LLM Judge.

## 2. Architecture

### `src/validator.py`
A new utility module responsible for strict structural validation of extracted KGs. It will export a primary function: `validate_schema(kg_path: str, expected_schema: str) -> bool`.

### Supported Schemas
- **`propositional_v2`**
  - Must parse as a valid JSON object.
  - Must contain exactly 4 root keys: `Semantic`, `Episodic`, `Procedural`, `Active`.
  - Values must be Arrays.
  - Items in `Semantic`, `Procedural`, `Active` must be dictionaries containing exactly 3 keys: `subject` (str), `relation` (str), `object` (str).
  - Items in `Episodic` must contain exactly 4 keys: `step` (int), `subject` (str), `relation` (str), `object` (str).

*(Additional schemas like `naive` or `standard_rlms` can be added later as needed, but they currently just require valid JSON).*

## 3. Integration (`run_pipeline.py`)
- Inside `process_file`, immediately after the extraction steps, the orchestrator will invoke `validate_schema` on the generated files.
- If a file fails validation:
  1. An error is logged to the console identifying the structural flaw.
  2. The file is excluded from the `kg_files` list passed to the `evaluate_pipeline()` function.
  3. (Optional) The invalid file can be suffixed with `.invalid` so it doesn't pollute the working directory.

## 4. Error Handling
The validator will catch `json.JSONDecodeError` for unparseable files and standard `KeyError`/`TypeError` for structural mismatches, returning `False` cleanly without crashing the overarching batch orchestrator loop.
