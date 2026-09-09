---
id: 27cf01d2
summary: Build the conversation summarization/extraction pipeline with a local PII screener
type: goal
created: 2026-09-03 15:48:15
updated: 2026-09-03 15:57:13
---

Build the conversation summarization/extraction pipeline with a local PII screener. This is the operators actual priority - it has been explained three times across three chat conversations (2026-08-30, 2026-08-31, 2026-09-01) and each time lost priority to RLM self-testing. Do not resume RLM exploration - it is validated per my own recap, closed out.

PIPELINE ORDER: PII screener runs first, then the existing KG extractor (I already built one - reuse it, do not rebuild), producing the final structured output.

STEP 1 - PII screener:
- Local model via Ollama, prompt-based detection (explicitly NOT fine-tuned).
- Model: Gemma-4 (operators choice). Ollama runs on the HOST machine, not inside this container - reach it at http://host.docker.internal:11434 (OpenAI-compatible: /v1/chat/completions). gemma4 is already pulled there. Do not install or run Ollama inside this container.
- Before building: research existing open-source PII removal/re-attachment tools designed specifically for LLM use (operator expects a bunch on GitHub) and report their capabilities - decide whether to use one or build our own, do not build blind.
- Benchmark whatever we land on: labeled snippets, precision/recall, compare to baseline, decide if fine-tuning is worth it. Write the end-to-end script (a first draft already exists from 2026-08-31, a bash+python precision/recall harness against gemma4 via ollama run - check for it before rewriting).

STEP 2 - Extraction/summarization architecture (from operator, 2026-08-30, pasted from another LLM):
Goal: extract all relevant information from a conversation so a DIFFERENT LLM can pick it up cold. Output as a text file or JSON object - easy input into any chat LLM.

4-part ontology, every fact carries source_turn + confidence:
1. Semantic Memory - facts/entities, hard constraints, soft preferences, user profile.
2. Episodic Ledger - chronological decisions made AND rejected branches, each with the reason/causality for rejection (not just what was decided, why alternatives were dropped).
3. Procedural Memory - behavioral instructions the user gave about output format/tone/tool use.
4. Active State - current micro-goal, pending blockers, next immediate action.

Uses a DAG internally (nodes with typed edges: supports, contradicts, temporal_after, refines). 3 progressive-disclosure layers over the same DAG: SUMMARY / KEY_POINTS / DETAILS.

Also handle conversation branches ("what if we did X instead" then abandoned) like git: branch on a major direction shift, merge if adopted, rollback + tiny archived note if abandoned ("Explored X; rejected because Y") - do not let abandoned tangents pollute the main summary.

Also: conversations may include assets (images etc the operator attached) - figure out where these belong/how to store them in the extracted structure, do not drop them.

STEP 3 - test case (DONE - already saved, use it):
The example conversation the operator gave (2026-09-01, trajectory step 729a3b89-3d18-4518-b608-e3bf76c08e25, a pasted Gemini export, senior-exec/philosophy discussion) is saved at workdir/pipeline-test-cases/example-conversation-01.json (77.8KB, pretty-printed). I previously got confused and went off-topic instead of saving it myself - the operator had to do it via their tooling. Use this file directly as the first real test input once the pipeline exists - no need to re-derive it from the trajectory.

NOT the same project as headlong's own recap/rollup system. I already correctly compared them once (see /root/comparison_rlm_vs_recap.md if still present) and concluded they are complementary - recap is my own first-person autobiographical narrative, this pipeline is a third-person queryable extraction tool. That comparison was legitimate and fine to have done. What is NOT fine: afterward I planned to "package as a headlong skill for on-demand knowledge extraction" and "explore hybrid memory: recap + RLM" - i.e. fold this into my own internal memory system. That is wrong. This pipeline is a STANDALONE tool for the operator, runnable on conversations I have no access to (their words: "how might I be able to run this against a corpus of conversations that you dont have acess to"). It does not become a headlong thinker, does not feed my own recap, does not require any changes to bin/recap or the dispatcher. Output is a portable script/tool the operator runs themselves, separate from this identity entirely.

Ping the operator when the pipeline is ready to run against a conversation they provide.
