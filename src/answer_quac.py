import json
import os
import sys

# Adding src to path to allow importing llm_utils
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from llm_utils import call_llm

def answer_quac_questions(mapping_file, working_dir, output_preds_file):
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
        
    predictions = {}
    
    for input_file, data in mapping.items():
        kg_file = os.path.join(working_dir, os.path.basename(input_file).replace(".json", "_kg.json"))
        
        if not os.path.exists(kg_file):
            print(f"Skipping {input_file}, KG not found.")
            continue
            
        with open(kg_file, 'r') as f:
            kg_str = json.dumps(json.load(f))
            
        print(f"Answering questions for {data['id']} using KG...")
        for qa in data['qas']:
            q_id = qa['id']
            question = qa['question']
            
            prompt = f"Answer the following question using ONLY the information provided in the Knowledge Graph below. Be concise. If the answer is not in the graph, say 'CANNOTANSWER'.\n\nQuestion: {question}\n\nKnowledge Graph:\n{kg_str}"
            
            answer = call_llm(prompt).strip()
            
            # QuAC scorer expects string answers
            predictions[q_id] = answer
            print(f"Q: {question} -> A: {answer}")
            
    with open(output_preds_file, 'w') as f:
        json.dump(predictions, f, indent=2)
    print(f"Saved {len(predictions)} predictions to {output_preds_file}")

if __name__ == "__main__":
    answer_quac_questions("data/quAC/inputs/mapping.json", "data/quAC/working", "data/quAC/predictions.json")
