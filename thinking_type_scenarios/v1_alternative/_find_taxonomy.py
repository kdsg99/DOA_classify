# -*- coding: utf-8 -*-
"""找最初的三维度定义：DOA 根目录清单 + 关键词扫描。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:\Users\kl001\.nanobot\DOA"
print("=== 根目录 ===")
for f in sorted(os.listdir(ROOT)):
    p = os.path.join(ROOT, f)
    print("  %-48s %s" % (f, ("%.1f KB" % (os.path.getsize(p) / 1024)) if os.path.isfile(p) else "<dir>"))

KEYS = ["认知操作", "内容执行", "结构组织", "元认知控制", "认知层", "维度", "dimension",
        "Meta", "Cognitive", "organization", "taxonomy", "类别"]
print("\n=== 关键词命中（文本类文件，排除我的新目录） ===")
hits = {}
for d, ds, fs in os.walk(ROOT):
    ds[:] = [x for x in ds if x not in ("thinking_type_scenarios", "llm_cache", "cache_v4", ".git")]
    for f in fs:
        if not f.endswith((".py", ".md", ".txt", ".ipynb", ".json", ".csv", ".html")):
            continue
        p = os.path.join(d, f)
        try:
            if os.path.getsize(p) > 3_000_000:
                continue
            t = open(p, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        got = [k for k in KEYS if k in t]
        if got:
            hits[os.path.relpath(p, ROOT)] = got
for k, v in sorted(hits.items()):
    print("  %-70s %s" % (k, ",".join(v)))
