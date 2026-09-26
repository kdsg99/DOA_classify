# -*- coding: utf-8 -*-
"""摸清 raw_data 的结构：扩样的原料在哪里、还缺什么。"""
import glob
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
D = r"C:\Users\kl001\.nanobot\DOA\signal_experts"
import pandas as pd                                             # noqa: E402

for f in sorted(glob.glob(os.path.join(D, "raw_data", "*.csv"))):
    df = pd.read_csv(f)
    print("=" * 100)
    print("%-28s %d 行 × %d 列" % (os.path.basename(f), len(df), len(df.columns)))
    print("  列：", list(df.columns))
    if len(df):
        r = df.iloc[0]
        for c in df.columns:
            v = str(r[c]).replace("\n", " ")
            print("   %-22s %s" % (c, v[:150]))
    print("  族分布：", df.dataset_id.value_counts().to_dict() if "dataset_id" in df else "n/a")
    for c in ["set", "strategy", "model", "primary", "primary_tag"]:
        if c in df:
            print("  %s 分布：%s" % (c, df[c].value_counts().head(6).to_dict()))
    break
print("\n全部文件行数与列数：")
for f in sorted(glob.glob(os.path.join(D, "raw_data", "*.csv"))):
    df = pd.read_csv(f)
    print("  %-26s %5d 行  列=%s" % (os.path.basename(f), len(df), ",".join(df.columns[:12])))
