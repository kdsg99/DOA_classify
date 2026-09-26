# -*- coding: utf-8 -*-
"""Pixel check: does the new headroom encoding (solid vs hollow) really render?"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import matplotlib                                               # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt                                 # noqa: E402
from PIL import Image                                           # noqa: E402

sys.path.insert(0, r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios")
import make_figs_tt6 as MF                                      # noqa: E402

fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
combos = [("L1", "K", "High"), ("L1", "R", "Low"), ("L2", "E", "High"), ("L3", "F", "Low")]
for i, (lvl, tgt, hr) in enumerate(combos):
    MF.bar(ax, i, 5.0, 10.0, lvl, tgt, hr, False)
ax.set_xlim(-12, 12)
ax.set_ylim(-0.7, 3.7)
fig.canvas.draw()
p = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\_enctest6.png"
fig.savefig(p, dpi=100)
plt.close(fig)
a = np.asarray(Image.open(p).convert("RGB"))
for i, (lvl, tgt, hr) in enumerate(combos):
    x_disp, y_disp = ax.transData.transform((3.5, float(i)))
    px, py = int(x_disp), int(a.shape[0] - y_disp)
    patch = a[py - 3:py + 4, px - 3:px + 4]
    print("%-8s %-5s RGB %s colours %d" % (lvl + "/" + tgt, hr,
          np.round(patch.reshape(-1, 3).mean(axis=0), 0).astype(int),
          len(np.unique(patch.reshape(-1, 3), axis=0))))
print("\nheadroom split:", {t: MF.ID2HR[t][0] for t in MF.ORDER})
