#!/bin/bash
set -a; source .env; set +a
echo "Running QA script to generate predictions from KG..."
python3 src/answer_quac.py

echo "Running official QuAC evaluation script..."
python3 data/quAC/evaluate-v0.2.py --val_file data/quAC/val_v0.2.json --model_preds data/quAC/predictions.json
