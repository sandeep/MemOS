import json
from src.llm_utils import call_llm

Q = "What is the sequence of logical steps the AI takes to reframe 'taste' as a data processing system for the user?"
TRUE_ANS = "The AI first defines the user's logical executive persona, then maps their engineering-driven need for objective criteria, diagnoses taste's lack of verifiable metrics, reframes taste as a specialized data processing system using sensory acuity and pattern recognition, elaborates its logic through shared lexicons and intersubjective agreements, and finally positions it as a coherent, measurable information-evaluation framework aligned with quantifiable value."

KG = """{
  "Procedural": [
    "Present 'taste' as a system that processes information and serves important social functions.",
    "Reframe 'taste' as a specialized form of data processing to resonate with an engineering mindset.",
    "Break down the system of 'taste' into foundational concepts including sensory acuity, pattern recognition, and shared lexicons.",
    "Convert subjective experiences to economic value through established lexicons and intersubjective agreements."
  ]
}"""

p1 = f"Answer this question using ONLY the Knowledge Graph below. Keep answers to 1 sentence. If the info is missing, say 'MISSING'.\n\nQuestion:\n{Q}\n\nKnowledge Graph:\n{KG}"
retrieved = call_llm(p1).strip()
print(f"RETRIEVED:\n{retrieved}\n")

p2 = f"Compare the TRUE Answer to the Retrieved Answer. Did the Retrieved Answer miss any critical facts? Give a score out of 100 as a SINGLE INTEGER ONLY on the first line, followed by a 1-sentence explanation on the next line.\n\nTRUE Answer:\n{TRUE_ANS}\n\nRetrieved Answer:\n{retrieved}"
judge = call_llm(p2).strip()
print(f"JUDGE:\n{judge}\n")
