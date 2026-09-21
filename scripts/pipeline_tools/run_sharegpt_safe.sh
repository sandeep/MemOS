#!/bin/bash
set -a; source .env; set +a
echo "Starting SAFE ShareGPT Benchmark..."

# Limit to first 10 files to avoid guardrails
count=0
for file in data/sharegpt/inputs_100/sharegpt_*.json; do
    if [ $count -ge 5 ]; then
        break
    fi
    
    # Only run if the rubric successfully generated
    rubric_file="${file%.json}_rubric.json"
    if [ -f "$rubric_file" ]; then
        echo "Processing $file..."
        python3 run_pipeline.py "$file"
        echo "Sleeping for 10 seconds to respect API guardrails..."
        sleep 10
        count=$((count+1))
    fi
done

echo "Safe Benchmark Complete."
