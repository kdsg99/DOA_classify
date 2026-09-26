# -*- coding: utf-8 -*-
"""整理目录：v1 版产物归档到 v1_alternative/，顶层留给 v2（三维）管线。"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios"
V1 = os.path.join(H, "v1_alternative")
os.makedirs(V1, exist_ok=True)
for f in ["tt_scenario_analysis.py", "make_figs.py", "summarize.py", "README.md",
          "scenarios.md", "_check_highlow.py", "_find_taxonomy.py", "_v2_scan.py"]:
    src = os.path.join(H, f)
    if os.path.exists(src):
        shutil.move(src, os.path.join(V1, f))
        print("moved", f)
for d in ["data"]:
    src = os.path.join(H, d)
    if os.path.isdir(src) and not os.listdir(src):
        os.rmdir(src)
        print("removed empty", d)
os.makedirs(os.path.join(H, "data"), exist_ok=True)
os.makedirs(os.path.join(H, "out"), exist_ok=True)
os.makedirs(os.path.join(H, "figs"), exist_ok=True)
print("\n顶层：", sorted(os.listdir(H)))
print("v1_alternative：", sorted(os.listdir(V1)))
