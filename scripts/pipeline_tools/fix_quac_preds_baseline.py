import json
with open("data/quAC/predictions_baseline.json", "r") as f:
    flat_preds = json.load(f)

dialogues = {}
for qid, text in flat_preds.items():
    did = qid.split("_q#")[0]
    if did not in dialogues:
        dialogues[did] = {"qid": [], "best_span_str": [], "yesno": [], "followup": []}
    dialogues[did]["qid"].append(qid)
    dialogues[did]["best_span_str"].append(text)
    dialogues[did]["yesno"].append("y")
    dialogues[did]["followup"].append("y")

with open("data/quAC/predictions_baseline.jsonl", "w") as f:
    for did, data in dialogues.items():
        f.write(json.dumps(data) + "\n")
