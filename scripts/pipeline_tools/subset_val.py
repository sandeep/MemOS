import json

with open("data/quAC/predictions.jsonl", "r") as f:
    predicted_dids = set(json.loads(line)["qid"][0].split("_q#")[0] for line in f)

with open("data/quAC/val_v0.2.json", "r") as f:
    val = json.load(f)

new_data = []
for p in val['data']:
    # each article has paragraphs
    new_paragraphs = []
    for par in p['paragraphs']:
        did = par['id']
        if did in predicted_dids:
            new_paragraphs.append(par)
    if new_paragraphs:
        p['paragraphs'] = new_paragraphs
        new_data.append(p)

val['data'] = new_data

with open("data/quAC/val_subset.json", "w") as f:
    json.dump(val, f)

print(f"Created subset with {len(predicted_dids)} predicted dialogues.")
