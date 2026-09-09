# BrainDrain: Recursive Language Model (RLM) Extractor

An experimental pipeline that dynamically generates Python code using a "Recursive Language Model" (RLM) prompt, executing it inside a sandboxed environment to extract structured knowledge graphs (or other compaction schemas) from massive conversational transcripts.

## Concept
Instead of statically parsing JSON with fixed python scripts, this project uses a meta-prompt to ask an LLM to **write its own chunking, parallelism, and extraction Python loop**. We then execute that generated loop inside a highly secure Podman sandbox.

## Features
- **Dynamic Prompt-to-Code**: The extraction script is written dynamically based on your schema prompts.
- **Resilient Checkpointing**: The generated scripts are instructed to aggressively save chunk-by-chunk state (`output_rlm.json`) to recover from rate limits.
- **Multi-Model Evaluator**: Built-in `evaluator.py` acts as an LLM Judge, comparing the compacted graph to the raw 8,000-character transcript.

## Setup

1. **Environment Variables**:
   Export your NVIDIA API key (or modify the code to point to local Ollama):
   ```bash
   export NVIDIA_API_KEY="nvapi-..."
   ```

2. **Start the Pipeline**:
   You must run the extractor inside Podman to ensure the dynamically generated Python code is securely sandboxed.
   
   ```bash
   # Run the 4-part KG extraction:
   podman run --rm -v $(pwd):/app -e NVIDIA_API_KEY=$NVIDIA_API_KEY braindrain-extractor python src/rlm_repl_extractor.py specs/test-case-conversation.json src/prompts/4_part_kg.txt
   
   # Or run the Propositional tuning:
   podman run --rm -v $(pwd):/app -e NVIDIA_API_KEY=$NVIDIA_API_KEY braindrain-extractor python src/rlm_repl_extractor.py specs/test-case-conversation.json src/prompts/propositional.txt
   ```

3. **Evaluate Results**:
   Once the `output_rlm.json` is generated, run the Judge to score the compaction fidelity:
   ```bash
   export NVIDIA_API_KEY="nvapi-..."
   python3 src/evaluator.py specs/test-case-conversation.json output_rlm.json
   ```

## Prompt Variations
Check `src/prompts/` for alternative compaction techniques (e.g. Propositional Extraction vs. 4-part Knowledge Graphs). You can quickly tune the methodology just by passing a different text prompt to the RLM.
