import os
import json
import glob
from src.extractor import extract_rlm
from src.extractor_recursive import extract as extract_recursive
import sys
sys.path.append(os.path.abspath("src"))
from llm_utils import call_llm

def translate_quac(limit=100):
    os.makedirs("data/quAC/inputs_100", exist_ok=True)
    with open("data/quAC/val_v0.2.json", 'r', encoding='utf-8') as f:
        quac_data = json.load(f)
    
    count = 0
    mapping = {}
    for article in quac_data['data']:
        for paragraph in article['paragraphs']:
            if count >= limit:
                break
            context = paragraph['context']
            did = paragraph['id']
            transcript = [{"role": "system", "content": f"Background Context: {context}"}]
            for qa in paragraph['qas']:
                transcript.append({"role": "user", "content": qa['question']})
                transcript.append({"role": "assistant", "content": qa['orig_answer']['text']})
                
            out_file = f"data/quAC/inputs_100/quac_{did}.json"
            with open(out_file, 'w') as f:
                json.dump(transcript, f, indent=2)
            mapping[out_file] = {"id": did, "qas": paragraph['qas']}
            count += 1
        if count >= limit:
            break
            
    with open("data/quAC/inputs_100/mapping.json", 'w') as f:
        json.dump(mapping, f, indent=2)
    return mapping

def generate_kgs(mapping):
    os.makedirs("data/quAC/working_100", exist_ok=True)
    
    for input_file in mapping.keys():
        base = os.path.basename(input_file).replace(".json", "")
        
        # 1. kg_naive
        naive_out = f"data/quAC/working_100/{base}_naive.json"
        if not os.path.exists(naive_out):
            try:
                extract_rlm(input_file, naive_out)
            except Exception as e:
                print(f"Failed naive {base}: {e}")
                
        # 2. kg_rlms
        rlms_out = f"data/quAC/working_100/{base}_rlms.json"
        if not os.path.exists(rlms_out):
            try:
                extract_recursive(input_file, None, rlms_out)
            except Exception as e:
                print(f"Failed rlms {base}: {e}")
                
        # 3. kg_propositional_v2
        v2_out = f"data/quAC/working_100/{base}_v2.json"
        if not os.path.exists(v2_out):
            try:
                extract_recursive(input_file, "src/prompts/propositional_v2_kg.txt", v2_out)
            except Exception as e:
                print(f"Failed v2 {base}: {e}")

def answer_questions(mapping, schema_suffix):
    preds = {}
    for input_file, data in mapping.items():
        base = os.path.basename(input_file).replace(".json", "")
        kg_file = f"data/quAC/working_100/{base}_{schema_suffix}.json"
        if not os.path.exists(kg_file):
            continue
        try:
            with open(kg_file, 'r') as f:
                kg_str = json.dumps(json.load(f))
        except:
            continue
            
        for qa in data['qas']:
            qid = qa['id']
            prompt = f"Answer the following question using ONLY the information provided in the Knowledge Graph below. Be concise. If the answer is not in the graph, say 'CANNOTANSWER'.\n\nQuestion: {qa['question']}\n\nKnowledge Graph:\n{kg_str}"
            answer = call_llm(prompt).strip()
            preds[qid] = answer
            
    # Write flat preds
    flat_path = f"data/quAC/preds_flat_{schema_suffix}.json"
    with open(flat_path, 'w') as f:
        json.dump(preds, f, indent=2)
        
    # Convert to JSONL format
    dialogues = {}
    for qid, text in preds.items():
        did = qid.split("_q#")[0]
        if did not in dialogues:
            dialogues[did] = {"qid": [], "best_span_str": [], "yesno": [], "followup": []}
        dialogues[did]["qid"].append(qid)
        dialogues[did]["best_span_str"].append(text)
        dialogues[did]["yesno"].append("y")
        dialogues[did]["followup"].append("y")
        
    jsonl_path = f"data/quAC/preds_100_{schema_suffix}.jsonl"
    with open(jsonl_path, "w") as f:
        for did, ddata in dialogues.items():
            f.write(json.dumps(ddata) + "\n")
            
def create_subset(mapping):
    with open("data/quAC/val_v0.2.json", "r") as f:
        val = json.load(f)
    
    predicted_dids = set(data["id"] for data in mapping.values())
    new_data = []
    for p in val['data']:
        new_paragraphs = [par for par in p['paragraphs'] if par['id'] in predicted_dids]
        if new_paragraphs:
            p['paragraphs'] = new_paragraphs
            new_data.append(p)
    val['data'] = new_data
    with open("data/quAC/val_subset_100.json", "w") as f:
        json.dump(val, f)

if __name__ == "__main__":
    print("Translating 100 QuAC dialogues...")
    mapping = translate_quac(100)
    print("Creating evaluation subset...")
    create_subset(mapping)
    print("Generating Knowledge Graphs...")
    generate_kgs(mapping)
    print("Answering questions for Naive...")
    answer_questions(mapping, "naive")
    print("Answering questions for RLMS...")
    answer_questions(mapping, "rlms")
    print("Answering questions for V2...")
    answer_questions(mapping, "v2")
    print("Done.")
