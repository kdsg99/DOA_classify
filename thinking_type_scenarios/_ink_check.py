# -*- coding: utf-8 -*-
"""粗查：每张图的 6 个面板区域是否都画上了东西（防止整块空白/NaN）。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
from PIL import Image                                           # noqa: E402

H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\figs"
for f in ["fig1_raw.png", "fig2_difficulty.png", "fig3_balanced.png",
          "fig1_raw_levels.png", "fig2_difficulty_levels.png"]:
    im = Image.open(H + "\\" + f).convert("L")
    a = np.asarray(im)
    ink = (a < 235).mean()                       # 非白像素比例
    h, w = a.shape
    cols = [round(ink_row) for ink_row in
            [((a[:, i * w // 6:(i + 1) * w // 6] < 235).mean() * 100) for i in range(6)]]
    print("%-28s %dx%d  ink=%.3f  per-column ink (%%): %s" % (f, w, h, ink, cols))
