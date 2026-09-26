# -*- coding: utf-8 -*-
"""找数据里是否存在名为 original 的分数列，以及各 CSV 表头里的难度相关列。"""
import csv
import glob
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
os.chdir(r"C:\Users\kl001\.nanobot\DOA")
hit = 0
for p in glob.glob("**/*.csv", recursive=True):
    try:
        h = next(csv.reader(open(p, encoding="utf-8", errors="ignore")))
    except Exception:
        continue
    low = [c.lower() for c in h]
    keep = [c for c in h if any(k in c.lower() for k in ("original", "plain", "orig", "difficulty"))]
    if keep:
        hit += 1
        print("%-72s %s" % (p[:72], keep))
    if hit > 25:
        break
