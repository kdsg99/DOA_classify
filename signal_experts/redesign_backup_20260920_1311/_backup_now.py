# -*- coding: utf-8 -*-
"""开工前备份 redesign 目录。"""
import os
import shutil
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
SRC = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
DST = SRC + r"_backup_" + time.strftime("%Y%m%d_%H%M")


def total_mb(p):
    s = 0
    for root, _d, fs in os.walk(p):
        for f in fs:
            try:
                s += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return s / 1048576


def count(p):
    n = 0
    for _r, _d, fs in os.walk(p):
        n += len(fs)
    return n


if os.path.exists(DST):
    print("backup already exists:", DST)
else:
    shutil.copytree(SRC, DST)
    print("copied ->", DST)
print("backup: %d files, %.1f MB" % (count(DST), total_mb(DST)))
print("source: %d files, %.1f MB" % (count(SRC), total_mb(SRC)))
