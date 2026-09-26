# -*- coding: utf-8 -*-
import sys

sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd

R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
d = pd.read_csv(R + r"\all_tasks_v4.csv")
for c in ["dataset_id", "dataset_title", "category", "difficulty", "original_difficulty",
          "level_label", "shift_direction", "model", "n_valid_scores"]:
    print("---", c, "nunique=", d[c].nunique(dropna=False))
    print(d[c].value_counts(dropna=False).head(15).to_string())
print("--- strategies x rows")
print(d.strategy.value_counts().to_string())
print("--- level_label x difficulty crosstab")
print(pd.crosstab(d.level_label, d.difficulty, dropna=False).to_string())
