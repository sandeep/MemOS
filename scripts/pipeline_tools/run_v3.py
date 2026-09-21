import os
import glob
from src.extractor_recursive import extract
from src.evaluator import evaluate_graph, generate_answer_key

def main():
    print("Running Propositional V3 (Temporal) on 5 ShareGPT files...")
    
    # Get the 5 files we successfully evaluated previously
    eval_dirs = glob.glob("data/working/evaluations/sharegpt_*")
    
    for eval_dir in eval_dirs:
        base_name = os.path.basename(eval_dir)
        input_file = f"data/sharegpt/inputs_100/{base_name}.json"
        
        if not os.path.exists(input_file):
            continue
            
        print(f"\nProcessing {base_name}...")
        
        # 1. Extract V3
        out_kg = f"data/working/evaluations/{base_name}/kg_v3_temporal.json"
        if not os.path.exists(out_kg):
            try:
                extract(input_file, "src/prompts/propositional_v3_temporal.txt", out_kg)
                print(f"Extraction successful: {out_kg}")
            except Exception as e:
                print(f"Extraction failed: {e}")
                continue
                
        # 2. Generate Ground Truth (if missing, though it should exist)
        transcript_path = input_file
        answer_key_path = os.path.join(eval_dir, "ground_truth_answer_key.json")
        if not os.path.exists(answer_key_path):
            generate_answer_key(transcript_path, eval_dir)
            
        # 3. Evaluate V3
        try:
            score, _, _, _ = evaluate_graph(transcript_path, out_kg, eval_dir)
            print(f"V3 Score for {base_name}: {score}%")
        except Exception as e:
            print(f"Evaluation failed: {e}")

if __name__ == "__main__":
    main()
