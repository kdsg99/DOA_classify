# -*- coding: utf-8 -*-
"""扩样可行性：源池路径是否存在、策略模板与分类器在哪。"""
import glob
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
D = r"C:\Users\kl001\.nanobot\DOA"
import pandas as pd                                             # noqa: E402

srcs = set()
for f in glob.glob(os.path.join(D, "signal_experts", "raw_data", "*.csv")):
    df = pd.read_csv(f)
    srcs |= set(df.source_file.dropna().unique())
print("source_file 取值：")
for s in sorted(srcs):
    print("   ", s)
cand = [D, r"C:\Users\kl001\.nanobot", r"D:\\", r"C:\Users\kl001\Desktop", r"C:\Users\kl001\Documents"]
print("\n存在性检查：")
for s in sorted(srcs):
    base = s.split("\\")[0]
    ok = [c for c in cand if os.path.exists(os.path.join(c, base))]
    print("   %-45s → %s" % (base, ok or "未找到"))
print("\nDOA 根目录下的 jsonl / py：")
for f in sorted(os.listdir(D)):
    if f.endswith((".jsonl", ".py", ".csv", ".md", ".ipynb")):
        print("   %-34s %8.1f KB" % (f, os.path.getsize(os.path.join(D, f)) / 1024))
print("\nconfig/prompts/strategies.py：")
p = os.path.join(D, "config", "prompts", "strategies.py")
txt = open(p, encoding="utf-8", errors="replace").read()
print(txt[:2400])
