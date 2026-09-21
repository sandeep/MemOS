import json
import os

def prep_sharegpt():
    os.makedirs("data/sharegpt/inputs_100", exist_ok=True)
    with open("data/sharegpt/real_conversations.json", "r") as f:
        data = json.load(f)
        
    for convo in data:
        cid = convo["id"].replace("/", "_")
        transcript = []
        for turn in convo["conversations"]:
            role = "user" if turn["from"] == "human" else "assistant"
            transcript.append({"role": role, "content": turn["value"]})
            
        with open(f"data/sharegpt/inputs_100/sharegpt_{cid}.json", "w") as f:
            json.dump(transcript, f, indent=2)
            
    print(f"Prepped {len(data)} ShareGPT transcripts.")

if __name__ == "__main__":
    prep_sharegpt()
