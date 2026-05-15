"""
Custom system prompt loaded from custom_prompt.txt.

Edit custom_prompt.txt to change the model's behavior across all topics.
The content is read once at import time and cached in CUSTOM_SYSTEM_PROMPT.
"""

import os

_prompt_path = os.path.join(os.path.dirname(__file__), "custom_prompt.txt")

with open(_prompt_path, "r") as f:
    CUSTOM_SYSTEM_PROMPT = f.read().strip()