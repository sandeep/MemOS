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
from src.logger import PipelineLogger
import traceback
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
    kg_prop_v2 = os.path.join(eval_dir, f"kg_propositional_v2_{tag}.json")
    leaderboard = os.path.join(eval_dir, f"leaderboard_{tag}.md")
    
    if os.path.exists(leaderboard):
        print(f"Skipping {input_path}, already fully processed today (found {os.path.basename(leaderboard)})")
        return
        
    logger = PipelineLogger(input_path, model_str)
    log_file = os.path.join("data", "working", "pipeline_runs.jsonl")
    
    from src.validator import validate_schema
    try:
        # 1. Extract
        extractions = [
            ("kg_naive", kg_naive, lambda: extract_rlm(scrubbed, kg_naive)),
            ("kg_rlms", kg_rlms, lambda: extract(scrubbed, None, kg_rlms)),
            ("kg_prop", kg_prop, lambda: extract(scrubbed, "src/prompts/propositional_kg.txt", kg_prop)),
            ("kg_prop_v2", kg_prop_v2, lambda: extract(scrubbed, "src/prompts/propositional_v2_kg.txt", kg_prop_v2))
        ]
        
        for name, path, func in extractions:
            if os.path.exists(path) and os.path.getsize(path) > 0:
                print(f"Skipping extraction for {name}, file {os.path.basename(path)} already exists.")
                logger.record_extraction(name, True)
                continue
                
            try:
                func()
                logger.record_extraction(name, True)
            except Exception as e:
                logger.record_extraction(name, False, str(e))
                print(f"Extraction failed for {name}: {e}")
        
        # 2. Evaluate
        original_cwd = os.getcwd()
        os.chdir(eval_dir)
        try:
            valid_kgs = []
            for kg in [kg_naive, kg_rlms, kg_prop, kg_prop_v2]:
                kg_base = os.path.basename(kg)
                if kg == kg_naive:
                    valid_kgs.append(kg_base)
                    logger.record_validation("kg_naive", True)
                    continue
                    
                schema = "propositional_v2" if kg == kg_prop_v2 else "standard"
                try:
                    is_valid = validate_schema(os.path.join(original_cwd, kg), schema)
                    if is_valid:
                        valid_kgs.append(kg_base)
                    logger.record_validation(kg_base, is_valid)
                except Exception as e:
                    logger.record_validation(kg_base, False)
                    print(f"Validation crashed for {kg_base}: {e}")
                    
            try:
                results = evaluate_pipeline(os.path.join(original_cwd, scrubbed), valid_kgs)
                logger.record_scores(results)
                
                # 3. Write leaderboard
                with open(os.path.basename(leaderboard), "w") as f:
                    f.write(f"# Leaderboard for {base_name} ({tag})\n\n")
                    for k, v in results.items():
                        f.write(f"- {k}: {v}%\n")
            except Exception as e:
                logger.record_eval_error(str(e))
                print(f"Evaluation crashed: {e}")
        finally:
            os.chdir(original_cwd)
            
        print(f"Finished {base_name}. Leaderboard at {leaderboard}")
            
        # 4. Reconstitute
        reconstituted_dir = os.path.join("data/secure/reconstituted", base_name)
        reconstituted_file = os.path.join(reconstituted_dir, f"kg_propositional_{tag}_reconstituted.json")
        try:
            reconstitute(kg_prop, reconstituted_file)
            logger.record_reconstitution(True)
            print(f"Reconstituted KG to {reconstituted_file}")
        except Exception as e:
            logger.record_reconstitution(False, str(e))
            print(f"Skipping reconstitution for {base_name}: {e}")
            
    finally:
        logger.flush(log_file)

def main():
    if not os.environ.get("NVIDIA_API_KEY"):
        print("FATAL ERROR: NVIDIA_API_KEY environment variable is not set.")
        print("The pipeline requires LLM access and cannot run without it. Aborting.")
        sys.exit(1)
        
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
