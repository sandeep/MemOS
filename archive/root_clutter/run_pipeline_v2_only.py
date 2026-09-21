import os, sys, datetime
from run_pipeline import copy_to_scrubbed
from src.extractor_rlms import extract
from src.validator import validate_schema
from src.evaluator import run_pipeline as evaluate_pipeline

def process_v2(input_path: str):
    filename = os.path.basename(input_path)
    base_name = os.path.splitext(filename)[0]
    eval_dir = os.path.join("data/working/evaluations", base_name)
    os.makedirs(eval_dir, exist_ok=True)
    
    scrubbed = copy_to_scrubbed(input_path)
    tag = datetime.datetime.now().strftime("%Y-%m-%d") + "_gemma4_31b"
    kg_prop_v2 = os.path.join(eval_dir, f"kg_propositional_v2_{tag}.json")
    
    print("Extracting V2 Graph in Podman...")
    extract(scrubbed, "src/prompts/propositional_v2_kg.txt", kg_prop_v2)
    
    if validate_schema(kg_prop_v2, "propositional_v2"):
        original_cwd = os.getcwd()
        os.chdir(eval_dir)
        print("Evaluating V2 Graph...")
        results = evaluate_pipeline(os.path.join(original_cwd, scrubbed), [os.path.basename(kg_prop_v2)])
        os.chdir(original_cwd)
        print(f"Final V2 Score: {results}")
    else:
        print("Schema validation failed!")

if __name__ == "__main__":
    process_v2("specs/test-case-conversation.json")
