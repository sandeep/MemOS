#!/bin/bash
set -a; source .env; set +a

echo "Running ShareGPT Ethics..."
python3 run_pipeline.py data/secure/inputs/sharegpt_ethics_01.json

echo "Running WildChat React..."
python3 run_pipeline.py data/secure/inputs/wildchat_react_01.json

echo "Custom Benchmark Complete."
