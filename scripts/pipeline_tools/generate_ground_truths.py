import os
import glob
import json
import time
import sys

sys.path.append(os.path.abspath("src"))
from evaluator import generate_answer_key

def main():
    print("Scaling up Ground Truth Generation to all 100 ShareGPT files...")
    input_files = glob.glob("data/sharegpt/inputs_100/sharegpt_*.json")
    
    count = 0
    for file in input_files:
        base_name = os.path.basename(file).replace(".json", "")
        eval_dir = f"data/working/evaluations/{base_name}"
        os.makedirs(eval_dir, exist_ok=True)
        
        answer_key_path = os.path.join(eval_dir, "ground_truth_answer_key.json")
        if os.path.exists(answer_key_path) and os.path.getsize(answer_key_path) > 0:
            continue
            
        print(f"Generating Ground Truth for {base_name}...")
        try:
            # We need to pass the transcript string to generate_answer_key
            with open(file, "r") as f:
                transcript_str = json.dumps(json.load(f))
            
            # This calls the LLM multiple times (3x per question)
            answer_key = generate_answer_key(transcript_str)
            
            # Save it
            with open(answer_key_path + ".tmp", "w") as f:
                json.dump(answer_key, f, indent=2)
            os.rename(answer_key_path + ".tmp", answer_key_path)
            
            print(f"Successfully generated Ground Truth for {base_name}.")
            count += 1
            
            # Sleep to respect API guardrails
            time.sleep(5)
            
        except Exception as e:
            print(f"Failed to generate Ground Truth for {base_name}: {e}")
            
    print(f"Finished generating {count} new Ground Truth answer keys.")

if __name__ == "__main__":
    main()
