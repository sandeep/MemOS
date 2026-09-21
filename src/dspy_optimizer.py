import os
import json
import dspy
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from evaluator import retrieve_answers, judge_answers

openrouter_key = os.environ.get("OPENROUTER_API_KEY")
if not openrouter_key:
    raise ValueError("OPENROUTER_API_KEY is missing. Source your .env file.")

# 1. Configure the LLMs (Student and Teacher)
# Student: The model we run in production (Fast, cheap, open-weights)
student_lm = dspy.LM(
    "openai/meta-llama/llama-3.1-70b-instruct", 
    api_base="https://openrouter.ai/api/v1", 
    api_key=openrouter_key
)

# Teacher: The model that writes the optimized instructions for the student (Frontier model)
teacher_lm = dspy.LM(
    "anthropic/claude-sonnet-latest", 
    api_base="https://openrouter.ai/api/v1", 
    api_key=openrouter_key
)

dspy.settings.configure(lm=student_lm)

# 2. Define the DSPy Signature
class ExtractCognitiveGraph(dspy.Signature):
    """
    MISSION: We are going to synthesize conversations between an AI agent and a human so that the conversation can be seamlessly continued later.
    Your goal is to reduce unnecessary content in the chat turns without losing any fidelity or conversational state.
    Extract the transcript into a flattened JSON Knowledge Graph with Temporal edges.
    """
    transcript = dspy.InputField(desc="The raw JSON conversational transcript")
    cognitive_graph_json = dspy.OutputField(desc="A 4-part JSON (semantic, episodic, procedural, active) containing flat lists of [Subject, Relation, Object] triples.")

# 3. Define the DSPy Metric (The LLM Judge)
def llm_judge_metric(example, pred, trace=None):
    try:
        eval_dir = f"data/working/evaluations/{example.file_id}"
        answer_key_path = os.path.join(eval_dir, "ground_truth_answer_key.json")
        
        if not os.path.exists(answer_key_path):
            return 0.0
            
        with open(answer_key_path, "r") as f:
            ground_truth = json.load(f)
            
        retrieved = retrieve_answers(pred.cognitive_graph_json)
        scores = judge_answers(ground_truth, retrieved)
        
        return float(sum(scores) / len(scores)) if scores else 0.0
    except Exception:
        return 0.0

# 4. Define the Module
class CognitiveExtractor(dspy.Module):
    def __init__(self):
        super().__init__()
        self.extractor = dspy.ChainOfThought(ExtractCognitiveGraph)
        
    def forward(self, transcript):
        return self.extractor(transcript=transcript)

def main():
    print("DSPy Optimizer initialized with Llama-3.1-70B (Student) and Claude 3.5 Sonnet (Teacher).")
    # Setup the optimizer (MIPRO)
    teleprompter = dspy.MIPROv2(
        metric=llm_judge_metric,
        auto="light", # Uses Teacher LM to generate instructions
        prompt_model=teacher_lm
    )
    print("Teleprompter ready. Awaiting Ground Truth completion to start training.")

if __name__ == "__main__":
    main()
