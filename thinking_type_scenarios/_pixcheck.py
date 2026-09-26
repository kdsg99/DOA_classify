# -*- coding: utf-8 -*-
"""Pixel-level check that solid/hollow + pattern really render (exact coordinates)."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import matplotlib                                               # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt                                 # noqa: E402
from PIL import Image                                           # noqa: E402

sys.path.insert(0, r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios")
import make_figs_enc as MF                                      # noqa: E402

fig, ax = plt.subplots(figsize=(6, 3), dpi=100)
combos = [("L1", "K", "Offensive"), ("L1", "R", "Defensive"), ("L2", "E", "Offensive"),
          ("L3", "F", "Defensive")]
for i, (lvl, tgt, nat) in enumerate(combos):
    MF.bar(ax, i, 5.0, 10.0, lvl, tgt, nat, False)
ax.set_xlim(-12, 12)
ax.set_ylim(-0.7, 3.7)
fig.canvas.draw()
W, H = fig.canvas.get_width_height()
p = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\_enctest.png"
fig.savefig(p, dpi=100)
plt.close(fig)
a = np.asarray(Image.open(p).convert("RGB"))

for i, (lvl, tgt, nat) in enumerate(combos):
    for fx in (0.4, 0.7):
        x_disp, y_disp = ax.transData.transform((5.0 * fx, float(i)))
        px, py = int(x_disp), int(a.shape[0] - y_disp)
        patch = a[py - 3:py + 4, px - 3:px + 4]
        print("%-9s %-9s x=%.1f  RGB %s  colours %d" % (
            lvl + "/" + tgt, nat, 5.0 * fx, np.round(patch.reshape(-1, 3).mean(axis=0), 0).astype(int),
            len(np.unique(patch.reshape(-1, 3), axis=0))))
