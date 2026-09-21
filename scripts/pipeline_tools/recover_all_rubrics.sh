#!/bin/bash
set -a; source .env; set +a
count=0
for file in data/sharegpt/inputs_100/sharegpt_*.json; do
    rubric_file="${file%.json}_rubric.json"
    if [ ! -f "$rubric_file" ]; then
        echo "Recovering $file..."
        python3 src/generate_rubric.py "$file"
        count=$((count+1))
    fi
done
echo "Recovered $count broken rubrics."
