import os
import json
import glob
from src.extractor_recursive import extract
from src.score_dialogre import calculate_f1

def flatten_v2_graph(kg_path):
    triples = []
    try:
        with open(kg_path, 'r') as f:
            data = json.load(f)
            for bucket in ["Semantic", "Episodic", "Procedural", "Active"]:
                # The pydantic models accept lowercased keys as well
                key = bucket if bucket in data else bucket.lower()
                for item in data.get(key, []):
                    # Handle both standard dictionary objects and potentially slightly malformed LLM outputs
                    if isinstance(item, dict):
                        sub = item.get("subject", "")
                        rel = item.get("relation", "")
                        obj = item.get("object", "")
                        if sub and rel and obj:
                            triples.append([sub, rel, obj])
    except Exception as e:
        print(f"Error parsing {kg_path}: {e}")
    return triples

def run_batch():
    input_files = sorted(glob.glob("data/dialogre/inputs/dialogre_test_*.json"))[:10]
    prompt_file = "src/prompts/propositional_v2_kg.txt"
    
    global_tp, global_fp, global_fn = 0, 0, 0
    
    os.makedirs("data/dialogre/working", exist_ok=True)
    
    print(f"Starting batch of {len(input_files)} dialogues...")
    for idx, input_path in enumerate(input_files):
        print(f"\n--- Processing Dialogue {idx+1}/10: {os.path.basename(input_path)} ---")
        
        # 1. Extract
        output_path = os.path.join("data/dialogre/working", os.path.basename(input_path).replace(".json", "_kg.json"))
        if not os.path.exists(output_path):
            extract(input_path, prompt_file, output_path)
        else:
            print(f"KG already exists: {output_path}")
            
        # 2. Flatten
        predicted_triples = flatten_v2_graph(output_path)
        
        # 3. Load Truth
        truth_path = os.path.join("data/dialogre/ground_truth", os.path.basename(input_path).replace(".json", "_truth.json"))
        with open(truth_path, 'r') as f:
            true_triples = json.load(f)
            
        # 4. Score this dialogue
        print(f"Extracted {len(predicted_triples)} triples. Truth has {len(true_triples)} triples.")
        
        true_set = set(tuple(str(x).lower() for x in t) for t in true_triples)
        pred_set = set(tuple(str(x).lower() for x in t) for t in predicted_triples)

        tp = len(true_set.intersection(pred_set))
        fp = len(pred_set - true_set)
        fn = len(true_set - pred_set)
        
        global_tp += tp
        global_fp += fp
        global_fn += fn
        
        print(f"Dialogue {idx+1} -> TP: {tp}, FP: {fp}, FN: {fn}")
        
    print("\n==============================")
    print("GLOBAL BATCH RESULTS (10 Dialogues)")
    print("==============================")
    precision = global_tp / (global_tp + global_fp) if (global_tp + global_fp) > 0 else 0.0
    recall = global_tp / (global_tp + global_fn) if (global_tp + global_fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    print(f"Global True Positives: {global_tp}")
    print(f"Global False Positives: {global_fp}")
    print(f"Global False Negatives: {global_fn}")
    print(f"Global Precision: {precision:.4f}")
    print(f"Global Recall: {recall:.4f}")
    print(f"Global F1 Score: {f1:.4f}")

if __name__ == "__main__":
    run_batch()
