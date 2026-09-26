# -*- coding: utf-8 -*-
"""去掉 command_record.md 中重复追加的本次条目（只保留一份）。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
P = r"C:\Users\kl001\.nanobot\command_record.md"
txt = open(P, encoding="utf-8").read()
marker = "\n## 2026-09-20 v4 效应量分析"
idx = txt.find(marker)
print("出现次数:", txt.count(marker), "首个位置:", idx, "总长:", len(txt))
if txt.count(marker) > 1:
    head = txt[:idx]
    body = txt[idx:]
    # 去掉重复块：第二份 marker 之前的所有内容 + 保留第一份到结尾
    second = body.find(marker, 1)
    fixed = head + body[:second].rstrip() + "\n"
    open(P, "w", encoding="utf-8").write(fixed)
    print("已去重 -> %.1f KB" % (len(fixed) / 1024))
else:
    print("无重复，未改动")
