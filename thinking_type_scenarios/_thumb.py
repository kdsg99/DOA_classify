# -*- coding: utf-8 -*-
"""生成缩略图用于自检（1600px 宽）。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image                                            # noqa: E402

H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\figs"
T = os.path.join(H, "thumbs")
os.makedirs(T, exist_ok=True)
for f in ["fig1_raw.png", "fig2_difficulty.png", "fig3_balanced.png"]:
    im = Image.open(os.path.join(H, f))
    im.thumbnail((1700, 1700))
    out = os.path.join(T, f.replace(".png", "_thumb.png"))
    im.save(out)
    print(out, im.size)
