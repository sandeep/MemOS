import os
import glob
import re
import csv

def main():
    output_csv = "data/working/master_results.csv"
    
    # Check if we need to write headers
    write_headers = not os.path.exists(output_csv)
    
    with open(output_csv, "w" if write_headers else "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        if write_headers:
            writer.writerow(["Evaluation_ID", "Timestamp", "Dataset", "Model_Architecture", "Score_Percent"])
            
        # Parse all leaderboard markdown files
        leaderboards = glob.glob("data/working/evaluations/*/leaderboard_*.md")
        for lb in leaderboards:
            eval_id = os.path.basename(os.path.dirname(lb))
            dataset = "sharegpt" if "sharegpt" in eval_id else "quac"
            
            with open(lb, "r") as f:
                content = f.read()
                
            # Regex to find lines like: - kg_naive_2026-09-20_200800_llama-3.1-70b.json: 66.0%
            matches = re.findall(r'- (kg_[a-zA-Z0-9_]+)_(\d{4}-\d{2}-\d{2}_\d{6})_.*\.json:\s*([\d\.]+)%', content)
            
            for model_arch, timestamp, score in matches:
                writer.writerow([eval_id, timestamp, dataset, model_arch, score])
                
    print(f"Aggregated all current results into {output_csv}")

if __name__ == "__main__":
    main()
