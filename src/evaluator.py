"""
evaluator.py
3-Stage Evaluator: (1) Answer Key (2) Retriever (3) Judge
Scores multiple KG files against a raw transcript.
"""
import json
import sys
import re
from llm_utils import call_llm

QUESTIONS = [
    "(Control) The user begins their message with a self-description that includes a specific personality identifier and two adjectives; what is the exact string the user uses for their personality type and cognitive style?",
    "(Semantic) What is the core conflict or objective vs subjective tension expressed by the user regarding taste-based professions?",
    "(Episodic) What is the sequence of logical steps the AI takes to reframe 'taste' as a data processing system for the user?",
    "(Procedural/Active) What is the immediate focus or unresolved question the AI is trying to address to bridge the gap for the user?"
]

def run_pipeline(transcript_file: str, kg_files: list):
    pass

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 src/evaluator.py <transcript.json> <kg_file1.json> [kg_file2.json ...]")
        sys.exit(1)
    run_pipeline(sys.argv[1], sys.argv[2:])
