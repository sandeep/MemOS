import os

def init_directories():
    directories = [
        "data/secure/inputs",
        "data/secure/reconstituted",
        "data/working/scrubbed_inputs",
        "data/working/evaluations"
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)
