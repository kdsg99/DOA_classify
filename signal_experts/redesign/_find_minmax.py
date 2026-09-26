# -*- coding: utf-8 -*-
"""找 minmax 输出目录，看扩样原料是否现成。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
for root in [r"C:\Users\kl001\.nanobot\DOA", r"C:\Users\kl001\Documents", r"D:\\"]:
    if not os.path.isdir(root):
        continue
    hits = []
    for d, ds, fs in os.walk(root):
        if "minmax" in d.lower():
            hits.append(d)
            ds[:] = []
        if len(hits) > 30:
            break
    print("根目录 %s → %d 个 minmax 目录" % (root, len(hits)))
    for h in hits[:30]:
        try:
            n = len(os.listdir(h))
        except Exception:
            n = -1
        print("   ", h, "（%d 个条目）" % n)
