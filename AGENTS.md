# Antigravity Operating Manual for brainDrain

1. **Test-Driven Development (TDD) Mandate**: Antigravity is strictly forbidden from running end-to-end container pipelines as a debugging mechanism. You must write an isolated `pytest` unit test and prove fixes work locally before ever touching Podman or `run_pipeline.py`.
2. **Never Celebrate Early**: Do not claim victory or celebrate until the user has fully confirmed the outputs and edge cases. Premature celebration indicates a lack of rigorous verification.
3. **Strict PR Workflow**: All code must be pushed to a branch and merged via PR. Agents are never allowed to merge their own work to `main`.
4. **Data Verification**: When making claims about LLM output scores, always inspect the raw execution logs to verify that the scores weren't artificial (e.g. 0.0% due to an API timeout).

