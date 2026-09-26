# -*- coding: utf-8 -*-
"""Recon 3: build a reliable task identity per row (task_id is only filled for mt_bench)."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\data\rows_v2.csv"
d = pd.read_csv(H)
cols = ["task_id", "problem", "task", "instruction", "wildbench_id", "session_id", "subject", "category",
        "second_turn", "set", "original_difficulty"]
for ds, g in d.groupby("dataset_id"):
    info = {c: int(g[c].notna().sum()) for c in cols}
    print("%-16s rows=%4d  %s" % (ds, len(g), info))
print()
print("sample non-null columns:")
for ds, g in d.groupby("dataset_id"):
    r = g.iloc[0]
    print("  %-16s task_id=%r problem=%r task=%r instruction=%r wb=%r sess=%r subj=%r cat=%r" % (
        ds, r.task_id, str(r.problem)[:40], str(r.task)[:40], str(r.instruction)[:30],
        r.wildbench_id, r.session_id, r.subject, r.category))
