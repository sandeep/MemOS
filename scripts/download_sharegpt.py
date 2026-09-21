#!/usr/bin/env python3
"""
Convenience CLI script to download a subset of real ShareGPT conversations from Hugging Face.
"""

import os
import sys

# Ensure repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.download_sharegpt import main

if __name__ == "__main__":
    main()
