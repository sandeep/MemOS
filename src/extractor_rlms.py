import os
import sys
import json
from rlm import RLM
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Set up Ollama's OpenAI-compatible endpoint
os.environ["OPENAI_API_KEY"] = "ollama"
os.environ["OPENAI_BASE_URL"] = "http://host.docker.internal:11434/v1"

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def scrub_pii(text: str) -> str:
    results = analyzer.analyze(text=text, language='en')
    return anonymizer.anonymize(text=text, analyzer_results=results).text

def extract(conversation_file: str):
    with open(conversation_file, 'r') as f:
        data = json.load(f)
    
    # Scrub the raw text
    safe_transcript = scrub_pii(json.dumps(data))
    
    print("Initializing RLMs library with Gemma-4...")
    # The RLM will execute its own Python REPL under the hood
    rlm = RLM(
        backend="openai",
        backend_kwargs={"model_name": "gemma4", "sampling_args": {"temperature": 0.0}},
        verbose=True
    )
    
    prompt = f"""You are a Knowledge Graph extraction system.
    I have provided the raw conversation transcript below.
    Your task is to write a python program to loop through this transcript and extract it into a 4-part JSON Knowledge Graph (Semantic, Episodic, Procedural, Active).
    
    Save the final output JSON to 'output_rlms.json'.
    Make sure your python code executes quickly (under 30 seconds).
    
    Transcript: {safe_transcript[:5000]}
    """
    
    print("Running RLM completion...")
    response = rlm.completion(prompt)
    print("RLM Execution complete.")

if __name__ == "__main__":
    if len(sys.argv) > 1: extract(sys.argv[1])
