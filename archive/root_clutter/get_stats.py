import os
import json

def get_stats(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        content = f.read()
    bytes_len = len(content.encode('utf-8'))
    words_len = len(content.split())
    # Approximation for tokens
    tokens = int(words_len * 1.3)
    return {"bytes": bytes_len, "words": words_len, "tokens": tokens}

files = ["specs/test-case-conversation.json", "output.json", "output_rlms.json"]
for f in files:
    stats = get_stats(f)
    print(f"{f}: {stats}")
