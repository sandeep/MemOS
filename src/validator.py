import re
from pydantic import ValidationError
from src.models import CognitiveGraphV1, CognitiveGraphV2

def extract_json_block(text: str) -> str:
    match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if match: return match.group(1).strip()
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    if match: return match.group(0).strip()
    return text

def validate_and_normalize(raw_text: str, expected_schema: str) -> str:
    clean_json = extract_json_block(raw_text)
    try:
        if expected_schema == "propositional_v2":
            model = CognitiveGraphV2.model_validate_json(clean_json)
        else:
            model = CognitiveGraphV1.model_validate_json(clean_json)
        return model.model_dump_json(indent=2)
    except ValidationError as e:
        raise ValueError(f"Pydantic Validation Error: {e}")

def validate_schema(kg_path: str, expected_schema: str) -> bool:
    try:
        with open(kg_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
            
        normalized_json = validate_and_normalize(raw_text, expected_schema)
        
        with open(kg_path, 'w', encoding='utf-8') as f:
            f.write(normalized_json)
            
        return True
    except (FileNotFoundError, ValueError) as e:
        print(f"Validation Error in {kg_path}: {e}")
        return False
