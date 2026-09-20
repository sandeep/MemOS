# Sources and Prior Research

This repository builds upon several domains of research in Large Language Model (LLM) context management, reasoning loops, and information extraction.

## 1. Context Compaction and Constraint Following
Our extraction pipeline addresses the dynamic information loss inherent in converting long-context dialogues into compact state representations. 
* **Reference:** *arXiv:2608.11242v1*
* **Context Compaction:** Prior work falls into three categories: (1) Context truncation (keeping only recent reflections), (2) Non-prompt-based compression (binary token classifiers/perplexity filters), and (3) Prompt-based LLM summarization. Our Knowledge Graph extraction pipeline falls into category 3, utilizing structured schemas to enforce lossless summarization.
* **Long Context Constraint Following:** While prior research (e.g., Zhao et al., 2025) demonstrates LLMs struggle to adhere to user preferences as contexts extend, and others evaluate instruction-following on static contexts, our Cognitive Graph framework specifically targets the dynamic information loss caused by prompt-based compaction.

## 2. Reasoning and Recursive Verification
The `RLMS` (Recursive Language Modeling System) architecture and the "RLM Sandwich" methodology tested in our pipelines rely heavily on forcing the LLM to generate intermediate reasoning tokens before final structured extraction.
* **Chain-of-Thought (CoT):** *Wei et al., 2022.* Forcing step-by-step reasoning tokens improves structured output reliability.
* **Scratchpads:** *Nye et al., 2021.* Utilizing intermediate computation "scratchpads" to map user intent before committing data to the final JSON structure.

## 3. Flat Relational Extraction (Triples)
Our breakthrough with `Propositional V2` proved that deeply nested hierarchical JSON schemas cause LLMs to fail due to syntax friction. 
* **Resource Description Framework (RDF) & DialogRE:** Academic benchmarks for Dialogue Relation Extraction (DialogRE) prove that LLMs extract conversational data much more accurately when constrained to flat, relational `(Subject, Relation, Object)` triples rather than deeply nested Object-Oriented architectures.

## 4. Autonomous Memory and Graph Architectures
To contextualize our pipeline against the current State-of-the-Art (SOTA) in agentic memory:
* **MemGPT / Letta:** *Packer et al., 2023.* Pioneered the "LLM-as-an-OS" paradigm, managing hierarchical memory blocks (Core vs. Archival). Our pipeline solves the extraction friction that agents like MemGPT face when trying to autonomously read/write complex state.
* **GraphRAG:** *Edge et al., 2024 (Microsoft).* Demonstrated that standard vector search (RAG) fails at global, multi-hop reasoning, and that LLMs require connected Knowledge Graphs for true comprehension.
* **DialogRE:** *Yu et al., 2020.* The foundational dataset and benchmark for Dialogue Relation Extraction, establishing the standard F1 scoring metric for multi-turn conversational extraction.
