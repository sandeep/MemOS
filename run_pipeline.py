import sys
import os
import shutil
import glob
import datetime

# Ensure src is in sys.path for internal module imports (e.g. llm_utils)
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from src.scaffold import init_directories
from src.extractor import extract_rlm
try:
    from src.extractor_rlms import extract
except ImportError:
    def extract(conversation_file: str, prompt_file: str = None, output_file: str = "output_rlms.json"):
        raise RuntimeError("extract from extractor_rlms unavailable: missing 'rlm' package")
from src.evaluator import run_pipeline as evaluate_pipeline
from src.reconstitutor import reconstitute

def copy_to_scrubbed(input_path: str) -> str:
    """Mock PII phase: just copy the file across the boundary."""
    filename = os.path.basename(input_path)
    scrubbed_path = os.path.join("data/working/scrubbed_inputs", filename)
    shutil.copy2(input_path, scrubbed_path)
    return scrubbed_path

def process_file(input_path: str):
    print(f"Processing {input_path}...")
    filename = os.path.basename(input_path)
    base_name = os.path.splitext(filename)[0]
    eval_dir = os.path.join("data/working/evaluations", base_name)
    os.makedirs(eval_dir, exist_ok=True)
    
    scrubbed = copy_to_scrubbed(input_path)
    print(f"Scrubbed to {scrubbed}")
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    model_str = "gemma4_31b" # Defaulting for now
    tag = f"{date_str}_{model_str}"
    
    kg_naive = os.path.join(eval_dir, f"kg_naive_{tag}.json")
    kg_rlms = os.path.join(eval_dir, f"kg_rlms_{tag}.json")
    kg_prop = os.path.join(eval_dir, f"kg_propositional_{tag}.json")
    leaderboard = os.path.join(eval_dir, f"leaderboard_{tag}.md")
    
    # 1. Extract
    extract_rlm(scrubbed, kg_naive)
    extract(scrubbed, None, kg_rlms)
    extract(scrubbed, "src/prompts/propositional_kg.txt", kg_prop)
    
    # 2. Evaluate
    # Temporarily cd into eval_dir so answer_key gets saved with the date and model tag
    original_cwd = os.getcwd()
    os.chdir(eval_dir)
    try:
        results = evaluate_pipeline(os.path.join(original_cwd, scrubbed), 
                                    [os.path.basename(kg_naive), os.path.basename(kg_rlms), os.path.basename(kg_prop)])
        
        # 3. Write leaderboard
        with open(os.path.basename(leaderboard), "w") as f:
            f.write(f"# Leaderboard for {base_name} ({tag})\n\n")
            for k, v in results.items():
                f.write(f"- {k}: {v}%\n")
    finally:
        os.chdir(original_cwd)
        
    print(f"Finished {base_name}. Leaderboard at {leaderboard}")
        
    # 4. Reconstitute
    reconstituted_dir = os.path.join("data/secure/reconstituted", base_name)
    reconstituted_file = os.path.join(reconstituted_dir, f"kg_propositional_{tag}_reconstituted.json")
    try:
        reconstitute(kg_prop, reconstituted_file)
        print(f"Reconstituted KG to {reconstituted_file}")
    except FileNotFoundError as e:
        print(f"Skipping reconstitution for {base_name}: {e}")

def main():
    init_directories()
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <file_path> or --all")
        sys.exit(1)
        
    arg = sys.argv[1]
    if arg == "--all":
        files = glob.glob("data/secure/inputs/*.json")
        for f in files:
            try:
                process_file(f)
            except Exception as e:
                print(f"Error processing {f}: {e}")
    else:
        if os.path.exists(arg):
            process_file(arg)
        else:
            print(f"File not found: {arg}")
            sys.exit(1)

if __name__ == "__main__":
    main()
