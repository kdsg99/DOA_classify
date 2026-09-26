# -*- coding: utf-8 -*-
"""列出产物大小，并复制到 figs 目录供邮件附件用。"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
SRC = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign\fig_effect"
DST = r"C:\Users\kl001\.nanobot\figs"
os.makedirs(DST, exist_ok=True)
tot = 0
for f in sorted(os.listdir(SRC)):
    p = os.path.join(SRC, f)
    s = os.path.getsize(p)
    tot += s
    print("%-44s %8.1f KB" % (f, s / 1024))
print("TOTAL %d files, %.1f MB" % (len(os.listdir(SRC)), tot / 1048576))
for f in sorted(os.listdir(SRC)):
    shutil.copy2(os.path.join(SRC, f), os.path.join(DST, "eff_" + f))
print("copied to", DST)
