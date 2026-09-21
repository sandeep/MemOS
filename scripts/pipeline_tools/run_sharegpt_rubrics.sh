#!/bin/bash
set -a; source .env; set +a
echo "Starting Rubric Generation for 100 ShareGPT Transcripts..."
for file in data/sharegpt/inputs_100/sharegpt_*.json; do
    # Skip if rubric already exists
    rubric_file="${file%.json}_rubric.json"
    if [ ! -f "$rubric_file" ]; then
        python3 src/generate_rubric.py "$file"
    fi
done
echo "Finished Rubric Generation."
