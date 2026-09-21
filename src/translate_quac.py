import json
import os

def translate_quac(input_path, output_dir, limit=5):
    os.makedirs(output_dir, exist_ok=True)
    with open(input_path, 'r', encoding='utf-8') as f:
        quac_data = json.load(f)

    count = 0
    mapping = {} # Store original dialogue ID mapping
    for article in quac_data['data']:
        for paragraph in article['paragraphs']:
            if count >= limit:
                break
            
            context = paragraph['context']
            dialogue_id = paragraph['qas'][0]['id'].split('_q#')[0] # base id
            
            transcript = [{"role": "system", "content": f"Background Context: {context}"}]
            
            for qa in paragraph['qas']:
                question = qa['question']
                # QuAC can have multiple valid answers, we take the original one for the transcript history
                answer = qa['orig_answer']['text']
                
                transcript.append({"role": "user", "content": question})
                transcript.append({"role": "assistant", "content": answer})
                
            out_file = os.path.join(output_dir, f"quac_{dialogue_id}.json")
            with open(out_file, 'w', encoding='utf-8') as out_f:
                json.dump(transcript, out_f, indent=2)
                
            mapping[out_file] = {
                "id": dialogue_id,
                "qas": paragraph['qas']
            }
            count += 1
        if count >= limit:
            break
            
    with open(os.path.join(output_dir, "mapping.json"), 'w') as f:
        json.dump(mapping, f, indent=2)
        
    print(f"Translated {count} QuAC dialogues into {output_dir}")

if __name__ == "__main__":
    translate_quac("data/quAC/val_v0.2.json", "data/quAC/inputs", limit=10)
