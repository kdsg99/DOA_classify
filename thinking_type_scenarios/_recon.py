# -*- coding: utf-8 -*-
"""Recon: what task-level content features / labels are available, and how convergent are the strategies?"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

B = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
for f in ["all_tasks_v2.csv", "all_tasks_v4.csv"]:
    d = pd.read_csv(B + "\\" + f)
    print("=== %s  %s" % (f, d.shape))
    print("cols:", list(d.columns))
    print("strategies:", d.strategy.value_counts().to_dict() if "strategy" in d else None)
    key = [c for c in ["dataset_id", "task_id", "model"] if c in d]
    print("distinct keys %s = %d" % (key, len(d.drop_duplicates(key))))
    print("datasets:", d.dataset_id.value_counts().to_dict())
    for c in ["thinking_type", "target", "primary_tag", "primary_group", "metadata_skill", "metadata_domain",
              "level_label", "difficulty", "category", "subject", "v4_primary", "primary_action"]:
        if c in d:
            print("  %-16s nuniq=%d  top: %s" % (c, d[c].nunique(), str(d[c].value_counts().head(6).to_dict())[:200]))
    print()
