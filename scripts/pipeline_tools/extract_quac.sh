#!/bin/bash
set -a; source .env; set +a
mkdir -p data/quAC/working

for file in data/quAC/inputs/quac_*.json; do
    filename=$(basename "$file")
    out_name="data/quAC/working/${filename%.json}_kg.json"
    
    echo "Extracting KG for $filename..."
    # We will write a tiny python runner to just call extract() 
done
