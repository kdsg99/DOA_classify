# -*- coding: utf-8 -*-
"""自检：bridge 附件解析 + MIME 映射 + 新图图例区是否有内容。"""
import importlib.util
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
from PIL import Image                                           # noqa: E402

# 1) bridge 语法与附件解析
spec = importlib.util.spec_from_file_location(
    "mb", r"C:\Users\kl001\.nanobot\workspace\mail-bridge\mail_bridge.py")
mb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mb)
print("bridge import OK; FILE_MIME =", mb.FILE_MIME)

D = r"C:\Users\kl001\.nanobot\deliver"
txt = ("正文第一行。\n"
       "[[attach: %s]]\n" % os.path.join(D, "DIFFICULTY_CORRECTION.md") +
       "[[attach: %s]]\n" % os.path.join(D, "make_figs_tt6.py") +
       "[[inline: %s]]\n" % os.path.join(D, "tt6_fig2_difficulty.png") +
       "[[attach: 不存在的文件.md]]\n尾行。\n")
clean, att, inl = mb.extract_outbound_attachments(txt, D)
print("attach ->", [a[0] for a in att], [len(a[1]) for a in att])
print("inline ->", [i[0] for i in inl], [len(i[1]) for i in inl])
print("clean body ->", repr(clean))

# 2) 图例区（右下角面板）墨迹检查
p = os.path.join(r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\figs_tt6", "fig2_difficulty.png")
a = np.asarray(Image.open(p).convert("L"))
h, w = a.shape
panel = a[int(h * 0.52):int(h * 0.99), int(w * 0.80):int(w * 0.995)]
ink = float((panel < 200).mean())
print("\nlegend panel %dx%d  dark-pixel share %.3f" % (panel.shape[1], panel.shape[0], ink))
