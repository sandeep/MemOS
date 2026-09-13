import sys
import os
import shutil
import glob
from src.scaffold import init_directories

def copy_to_scrubbed(input_path: str) -> str:
    """Mock PII phase: just copy the file across the boundary."""
    filename = os.path.basename(input_path)
    scrubbed_path = os.path.join("data/working/scrubbed_inputs", filename)
    shutil.copy2(input_path, scrubbed_path)
    return scrubbed_path

def process_file(input_path: str):
    print(f"Processing {input_path}...")
    scrubbed = copy_to_scrubbed(input_path)
    # Future tasks will hook extractors here
    print(f"Scrubbed to {scrubbed}")

def main():
    init_directories()
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <file_path> or --all")
        sys.exit(1)
        
    arg = sys.argv[1]
    if arg == "--all":
        files = glob.glob("data/secure/inputs/*.json")
        for f in files:
            process_file(f)
    else:
        if os.path.exists(arg):
            process_file(arg)
        else:
            print(f"File not found: {arg}")

if __name__ == "__main__":
    main()
