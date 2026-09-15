# Propositional Hybrid V2: Cognitive Triples

## Motivation
The V1 Propositional Knowledge Graph scored poorly on the LLM Judge (1.0% avg). While it successfully captured dense, atomic facts (the "propositional advantage"), it stored them as disconnected string arrays. This destroyed the relational context (edges) and narrative timeline that the Retriever LLM requires to answer complex, multi-hop reasoning questions.

We need a schema that retains the high-fidelity density of atomic facts, while restoring the traversable graph structure. 

## Brainstormed Alternatives

### Option A: The "Graph of Propositions"
*   **Concept:** Strict node-edge-node graph, where nodes are full factual statements rather than simple nouns.
*   **Example:** `["User requires objective metrics"] -> [CONFLICTS_WITH] -> ["Taste relies on subjective feeling"]`
*   **Motivation:** Forces explicit logical operators between complex ideas.

### Option B: The "Annotated Standard Graph"
*   **Concept:** Standard noun-based Knowledge Graph, but every edge contains an array of `supporting_propositions` providing dense context.
*   **Example:** Edge `User -> [is skeptical of] -> Taste` with metadata `["User states taste lacks metrics"]`.
*   **Motivation:** Retains the familiar standard graph structure but injects density into the edges.

### Option C: The "Chronological Propositional Log" (Triple-Buckets) - **[SELECTED]**
*   **Concept:** Retains the novel 4-bucket Cognitive Architecture (Semantic, Episodic, Procedural, Active), but formats the contents inside each bucket as explicit Triples `[Subject, Relation, Object]` with chronological step IDs.
*   **Example:** `{"bucket": "Episodic", "step": 1, "subject": "User", "relation": "expressed_skepticism_about", "object": "unquantifiable metrics"}`
*   **Motivation:** Fusing human memory buckets with formal graph triples is a highly novel "Cognitive Knowledge Graph." It perfectly preserves the narrative timeline (via `step: 1, 2...` in Episodic) which LLM Judges desperately need to answer "sequence of events" questions, while providing the rigid graph structure (Subject-Relation-Object) needed to answer factual questions accurately.

## Implementation Plan for Option C
1. Create `src/prompts/propositional_v2_kg.txt` instructing the RLM to output the Triple-Bucket schema.
2. Run the extraction using this new prompt to generate `kg_propositional_v2.json`.
3. Run the evaluator exclusively on `kg_propositional_v2.json` to see if the LLM Judge scores it higher than V1.
