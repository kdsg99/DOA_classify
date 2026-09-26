# -*- coding: utf-8 -*-
"""tt7 自检：像素级编码 + 新维度与 level/target 的冗余度。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402
import matplotlib                                               # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt                                 # noqa: E402
from PIL import Image                                           # noqa: E402

H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios"
sys.path.insert(0, H)
import make_figs_tt7 as MF                                      # noqa: E402


def cv(a, b):
    ct = pd.crosstab(pd.Series(list(a)).values, pd.Series(list(b)).values).values.astype(float)
    n = ct.sum()
    exp = ct.sum(1, keepdims=True) @ ct.sum(0, keepdims=True) / n
    chi2 = ((ct - exp) ** 2 / np.where(exp == 0, np.nan, exp)).sum()
    return float(np.sqrt((chi2 / n) / (min(ct.shape) - 1)))


lv = [t.split("-")[0] for t in MF.ORDER]
tg = [t.split("-")[1] for t in MF.ORDER]
d3 = [MF.ID2D3[t] for t in MF.ORDER]
print("dim3 labels:", dict(zip(MF.ORDER, d3)))
print("split:", pd.Series(d3).value_counts().to_dict())
print("Cramer V  dim3|level = %.2f   dim3|target = %.2f" % (cv(d3, lv), cv(d3, tg)))
print("per-level:", pd.crosstab(pd.Series(lv), pd.Series(d3)).to_dict())
print("per-target:", pd.crosstab(pd.Series(tg), pd.Series(d3)).to_dict())

fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
combos = [("L1", "K", "Continuation"), ("L1", "R", "FromScratch"),
          ("L2", "E", "Continuation"), ("L3", "F", "FromScratch")]
for i, (l, t, q) in enumerate(combos):
    MF.bar(ax, i, 5.0, 10.0, l, t, q, False)
ax.set_xlim(-12, 12)
ax.set_ylim(-0.7, 3.7)
p = H + r"\_enctest7.png"
fig.savefig(p, dpi=100)
fig.canvas.draw()
a = np.asarray(Image.open(p).convert("RGB"))
for i, (l, t, q) in enumerate(combos):
    px, py = ax.transData.transform((3.5, float(i)))
    patch = a[int(a.shape[0] - py) - 3:int(a.shape[0] - py) + 4, int(px) - 3:int(px) + 4]
    print("%-9s %-13s mean RGB %s  distinct colours %d" % (
        l + "/" + t, q, np.round(patch.reshape(-1, 3).mean(axis=0), 0).astype(int),
        len(np.unique(patch.reshape(-1, 3), axis=0))))
plt.close(fig)
