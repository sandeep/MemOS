import os
import glob
from src.extractor_recursive import extract

def main():
    os.makedirs("data/quAC/working", exist_ok=True)
    files = glob.glob("data/quAC/inputs/quac_*.json")
    for f in files:
        if "mapping.json" in f:
            continue
        out_path = os.path.join("data/quAC/working", os.path.basename(f).replace(".json", "_kg.json"))
        if not os.path.exists(out_path):
            print(f"Extracting KG for {f} -> {out_path}")
            extract(f, "src/prompts/propositional_v2_kg.txt", out_path)
            
if __name__ == "__main__":
    main()
