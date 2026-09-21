#!/bin/bash
set -a; source .env; set +a
echo "1. Extracting Baseline KGs..."
python3 run_quac_baseline.py
echo "2. Answering Questions..."
python3 answer_quac_baseline.py
echo "3. Formatting Predictions..."
python3 fix_quac_preds_baseline.py
echo "4. Scoring Baseline..."
python3 data/quAC/evaluate-v0.2.py --val_file data/quAC/val_subset.json --model_output data/quAC/predictions_baseline.jsonl
