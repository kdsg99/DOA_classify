# -*- coding: utf-8 -*-
"""分类器/缓存/模型可用性盘点。"""
import glob
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
D = r"C:\Users\kl001\.nanobot\DOA"
for f in ["signal_experts\\classifier.py", "signal_experts\\classified_paint.py",
          "signal_experts\\redesign\\classify_v4.py"]:
    p = os.path.join(D, f)
    if not os.path.exists(p):
        print("（缺）", f)
        continue
    t = open(p, encoding="utf-8", errors="replace").read()
    print("=" * 100)
    print(f, "%.1f KB" % (len(t) / 1024))
    print(t[:1500])
c = glob.glob(os.path.join(D, "signal_experts", "llm_cache", "*.json"))
print("=" * 100)
print("llm_cache 文件数：", len(c))
if c:
    j = json.load(open(c[0], encoding="utf-8", errors="replace"))
    print("样本键：", list(j)[:12])
    s = json.dumps(j, ensure_ascii=False)[:700]
    print("样本内容：", s)
