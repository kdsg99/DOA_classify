# -*- coding: utf-8 -*-
"""关键事实核对：标签是否按任务固定；PRESSURE 的数学题集为何更少更易。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
R = r"C:\Users\kl001\.nanobot\DOA\signal_experts\redesign"
import pandas as pd                                             # noqa: E402

df = pd.read_csv(R + r"\all_tasks_v4.csv")
key = ["dataset_id", "task_id"]
p = df.groupby(key)["primary"].nunique()
print("同一 (族, 题号) 行数：%d；primary 跨策略不一致的：%d（%.1f%%）"
      % (len(p), (p > 1).sum(), 100 * (p > 1).mean()))
t = df.groupby(key)["task"].nunique()
print("同一 (族, 题号) 的 task 文本不一致的：%d（%.1f%%）" % ((t > 1).sum(), 100 * (t > 1).mean()))
pl = df.groupby(key)["plain_minmax"].nunique()
print("同一 (族, 题号) 的 plain 不一致的：%d（%.1f%%）" % ((pl > 1).sum(), 100 * (pl > 1).mean()))

m = df[df.dataset_id == "chat_math500"]
P = set(m[m.strategy == "PRESSURE"].task_id)
O = set(m[m.strategy != "PRESSURE"].task_id)
print("\nchat_math500：PRESSURE 题号 %d 个，其它策略题号 %d 个，交集 %d，PRESSURE 独有 %d"
      % (len(P), len(O), len(P & O), len(P - O)))
mp = m[m.strategy == "PRESSURE"]
print("PRESSURE 数学行 plain 分布：", (100 * mp.plain_minmax).round(0).describe()[["min", "25%", "50%", "75%", "max"]].to_dict())
print("其它策略数学行 plain 中位数：%.0f" % (100 * m[m.strategy != "PRESSURE"].plain_minmax.median()))
print("PRESSURE 数学题号是否有交集内的难例：", [ (i, round(100*x,0)) for i, x in
      m[(m.strategy == "PRESSURE") & (m.task_id.isin(P & O))][["task_id", "plain_minmax"]].drop_duplicates().values[:10]])
# 每策略覆盖的题号数
print("\n每策略覆盖题号数（按族）：")
print(df.pivot_table(index="dataset_id", columns="strategy", values="task_id", aggfunc="nunique").fillna(0).astype(int).to_string())
print("\n各族独立题号数：%d" % df.groupby("dataset_id").task_id.nunique().sum(), df.groupby("dataset_id").task_id.nunique().to_dict())
