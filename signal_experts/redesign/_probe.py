# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from classify_v2 import classify_one

probes = [
 {"task": "If you have just overtaken the second person in a race, what is your current position?",
  "dataset_id": "mt_bench", "category": "reasoning"},
 {"task": "", "problem": "Find all real numbers x such that x^2+3x+1=0 and x>0, express in radical form.",
  "dataset_id": "chat_math500", "subject": "Algebra", "level_label": "Level 4"},
 {"task": "Write a travel blog post about a recent trip to Hawaii, highlighting cultural experiences.",
  "dataset_id": "mt_bench", "category": "writing"},
 {"task": "Given records of stock prices, extract the highest and lowest closing prices per month in 2022. Return as a CSV string.",
  "dataset_id": "mt_bench", "category": "extraction"},
 {"task": "Write a simple website in HTML. When a user clicks the button, it shows a random joke from a list of 4 jokes.",
  "dataset_id": "mt_bench", "category": "coding"},
 {"task": "Please take on the role of a relationship coach and offer suggestions for resolving their issues.",
  "dataset_id": "mt_bench", "category": "roleplay"},
 {"task": "What is the central dogma of molecular biology? What processes are involved? Who named this?",
  "dataset_id": "mt_bench", "category": "stem"},
 {"task": "Imagine you have a FEN notation of a chessboard. How can you draw a board to show this state in LATEX? Create LATEX code.",
  "dataset_id": "llama_flask", "metadata_domain": "Technology"},
 {"task": "Solve the following math problem step by step. A train travels 120 km in 2 hours...",
  "dataset_id": "mt_bench", "category": "math"},
 {"task": "Classify the sentiment of the following review as positive or negative: 'The food was cold.'",
  "dataset_id": "chat_flask", "metadata_skill": "Comprehension"},
]

for p in probes:
    tid = classify_one(p)
    print(tid, "|", str(p.get("task") or p.get("problem"))[:75])
