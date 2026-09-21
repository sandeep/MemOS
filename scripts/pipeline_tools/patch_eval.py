import re

with open('src/evaluator.py', 'r') as f:
    content = f.read()

# Replace hardcoded QUESTIONS block
content = re.sub(r'QUESTIONS = \[\n.*?\]\n', '', content, flags=re.DOTALL)

new_functions = """
def get_questions(transcript_path):
    rubric_path = transcript_path.replace(".json", "_rubric.json")
    import os, json
    if os.path.exists(rubric_path):
        with open(rubric_path, 'r') as f:
            data = json.load(f)
            questions = []
            for item in data:
                if isinstance(item, dict) and "question" in item:
                    questions.append(f"({item.get('domain', 'Domain')}) {item['question']}")
                elif isinstance(item, str):
                    questions.append(item)
            return questions
    return [
        "(Control) The user begins their message with a self-description that includes a specific personality identifier and two adjectives; what is the exact string the user uses for their personality type and cognitive style?",
        "(Control) What specific technology company or ecosystem is repeatedly used as the primary historical analogy for curating taste?",
        "(Control) What is the specific title or role of the user (e.g., SVP/CPO) mentioned in the conversation?",
        "(Semantic) What is the core conflict or objective vs subjective tension expressed by the user regarding taste-based professions?",
        "(Semantic) How does the AI define 'taste' functionally rather than aesthetically? What is its definition of taste as a system?",
        "(Semantic) According to the dialogue, what is the critical difference between 'intersubjective agreement' and 'objective truth'?",
        "(Episodic) What is the sequence of logical steps the AI takes to reframe 'taste' as a data processing system for the user?",
        "(Episodic) At what point in the conversation does the focus shift from philosophical definitions of taste to economic or systemic value creation?",
        "(Episodic) Describe the user's initial frustration or premise when the conversation started compared to where it ended.",
        "(Procedural) What are the specific, step-by-step mechanisms proposed to convert subjective quality into economic worth?",
        "(Procedural) What are the foundational rules or guidelines (like the 'Human Interface Guidelines' analogy) required to curate a taste-based platform?",
        "(Procedural) How is a developer or creator supposed to interact with the 'App Store of Taste' according to the proposed system?",
        "(Active) What is the immediate focus or unresolved question the AI is trying to address to bridge the gap for the user at the end of the text?",
        "(Active) What actionable goal or next step is the user attempting to achieve by dissecting the mechanics of taste?",
        "(Active) What remains the biggest blocker or unproven assumption in the AI's proposed system of taste?"
    ]

"""

content = content.replace("def generate_answer_key(", new_functions + "def generate_answer_key(")

# Update usages of QUESTIONS
content = content.replace("for i, q in enumerate(QUESTIONS):", "QUESTIONS = get_questions(transcript_path)\n    for i, q in enumerate(QUESTIONS):")

with open('src/evaluator.py', 'w') as f:
    f.write(content)
