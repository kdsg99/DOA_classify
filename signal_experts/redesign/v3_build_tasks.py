# -*- coding: utf-8 -*-
"""Build the unique-task table used by the v3 taxonomy labelling.
Deduplicates by (dataset_id, task_id) *and* by text hash (flask tasks are repeated
across model variants), producing v3_tasks.csv."""
import os, sys, hashlib, glob
import pandas as pd
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

SE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(SE, "raw_data")

frames = []
for f in sorted(glob.glob(os.path.join(RAW, "*.csv"))):
    d = pd.read_csv(f)
    d["strategy"] = os.path.basename(f).split("_")[0].upper()
    d["set"] = "high" if "_high" in f else "low"
    frames.append(d)
df = pd.concat(frames, ignore_index=True)

keep = ["dataset_id", "task_id", "task", "problem", "instruction", "category", "primary_group",
        "primary_tag", "metadata_domain", "metadata_skill", "subject", "level_label"]
tasks = df.sort_values(["dataset_id", "task_id"]).drop_duplicates(["dataset_id", "task_id"])[keep].copy()
def _s(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return str(v)

tasks["text"] = [f"{_s(a)}\n{_s(b)}\n{_s(c)}" for a, b, c
                 in zip(tasks["task"], tasks["problem"], tasks["instruction"])]
tasks["text_hash"] = tasks["text"].map(lambda s: hashlib.md5(s.encode("utf-8")).hexdigest())

before = len(tasks)
tasks = tasks.drop_duplicates("text_hash").reset_index(drop=True)
print(f"unique (dataset,task)={before} -> unique text={len(tasks)}")
tasks.to_csv(os.path.join(HERE, "v3_tasks.csv"), index=False)
print("saved ->", os.path.join(HERE, "v3_tasks.csv"))
print(tasks.groupby("dataset_id").size().to_dict())
