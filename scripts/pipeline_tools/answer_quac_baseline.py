import json
import os
import sys
sys.path.append(os.path.abspath("src"))
from llm_utils import call_llm

def answer_quac_questions(mapping_file, working_dir, output_preds_file):
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
        
    predictions = {}
    
    for input_file, data in mapping.items():
        kg_file = os.path.join(working_dir, os.path.basename(input_file).replace(".json", "_baseline_kg.json"))
        
        if not os.path.exists(kg_file):
            continue
            
        with open(kg_file, 'r') as f:
            kg_str = json.dumps(json.load(f))
            
        for qa in data['qas']:
            q_id = qa['id']
            question = qa['question']
            
            prompt = f"Answer the following question using ONLY the information provided in the Knowledge Graph below. Be concise. If the answer is not in the graph, say 'CANNOTANSWER'.\n\nQuestion: {question}\n\nKnowledge Graph:\n{kg_str}"
            answer = call_llm(prompt).strip()
            predictions[q_id] = answer
            
    with open(output_preds_file, 'w') as f:
        json.dump(predictions, f, indent=2)

if __name__ == "__main__":
    answer_quac_questions("data/quAC/inputs/mapping.json", "data/quAC/working", "data/quAC/predictions_baseline.json")
