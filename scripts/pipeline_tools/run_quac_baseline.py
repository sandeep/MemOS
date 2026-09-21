import os
import glob
import json
from src.extractor_recursive import extract

def main():
    files = glob.glob("data/quAC/inputs/quac_*.json")
    for f in files:
        if "mapping.json" in f:
            continue
        out_path = os.path.join("data/quAC/working", os.path.basename(f).replace(".json", "_baseline_kg.json"))
        if not os.path.exists(out_path):
            print(f"Extracting Baseline KG for {f} -> {out_path}")
            extract(f, "src/prompts/propositional_kg.txt", out_path)

if __name__ == "__main__":
    main()
