#!/bin/bash
set -a; source .env; set +a
echo "Starting 100-Conversation Batch..."
python3 run_quac_100.py

echo "--- EVALUATING KG_NAIVE ---"
python3 data/quAC/evaluate-v0.2.py --val_file data/quAC/val_subset_100.json --model_output data/quAC/preds_100_naive.jsonl > data/quAC/score_naive_100.txt
cat data/quAC/score_naive_100.txt

echo "--- EVALUATING KG_RLMS ---"
python3 data/quAC/evaluate-v0.2.py --val_file data/quAC/val_subset_100.json --model_output data/quAC/preds_100_rlms.jsonl > data/quAC/score_rlms_100.txt
cat data/quAC/score_rlms_100.txt

echo "--- EVALUATING KG_PROPOSITIONAL_V2 ---"
python3 data/quAC/evaluate-v0.2.py --val_file data/quAC/val_subset_100.json --model_output data/quAC/preds_100_v2.jsonl > data/quAC/score_v2_100.txt
cat data/quAC/score_v2_100.txt

echo "Batch 100 Complete."
