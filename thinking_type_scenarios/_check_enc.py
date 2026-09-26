# -*- coding: utf-8 -*-
"""Verify the three-dimension encoding actually lands on the bars (no eyes needed)."""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios"
sys.path.insert(0, HERE)
import pandas as pd                                             # noqa: E402
import matplotlib                                               # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt                                 # noqa: E402
import make_figs_enc as MF                                      # noqa: E402
from taxonomy_v2 import ID2LEVEL, ID2TARGET                     # noqa: E402

print("target hatch map:", MF.TARGET_HATCH)
fig, ax = plt.subplots()
combos = [("L1", "K", "Offensive"), ("L1", "R", "Defensive"), ("L2", "E", "Offensive"),
          ("L3", "F", "Defensive")]
for i, (lvl, tgt, nat) in enumerate(combos):
    MF.bar(ax, i, 5.0, 20.0, lvl, tgt, nat, False)
for p, (lvl, tgt, nat) in zip(ax.patches, combos):
    print("  %s/%s/%s -> hatch=%r facecolor=%r ls=%r alpha=%.2f" % (
        lvl, tgt, nat, p.get_hatch(), p.get_facecolor(), p.get_linestyle(), p.get_alpha()))
plt.close(fig)

R = pd.read_csv(os.path.join(HERE, "out", "cells_3dims.csv"))
print("\nnature per strategy x type (O=offensive, D=defensive):")
tab = R.assign(v=R.nature.str[0]).pivot(index="thinking_type", columns="strategy", values="v")
order = ["L1-K", "L1-R", "L1-E", "L1-F", "L2-K", "L2-R", "L2-E", "L2-F",
         "L3-K", "L3-R", "L3-E", "L3-F"]
print(tab.reindex(order).to_string())
print("\ncounts:", R.groupby(["strategy", "nature"]).size().unstack(fill_value=0).to_string())
print("\nlevel colours:", MF.LEVEL_COLOR)
print("target hatch:", MF.TARGET_HATCH)
