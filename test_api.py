import sys
import os
sys.path.append(os.path.abspath("src"))
from llm_utils import call_llm

try:
    print(call_llm("Reply with the word 'Alive'."))
except Exception as e:
    print(f"FAILED: {e}")
