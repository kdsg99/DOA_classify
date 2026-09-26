# -*- coding: utf-8 -*-
"""给第三维度候选做冗余度体检：与 level / target 的关联强度 + 各型取值。"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
import pandas as pd                                             # noqa: E402

ORDER = ["L1-K", "L1-R", "L1-E", "L1-F", "L2-K", "L2-R", "L2-E", "L2-F",
         "L3-K", "L3-R", "L3-E", "L3-F"]
d = pd.read_csv(r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\data\rows_v2.csv")
d = d[d.thinking_type.isin(ORDER)]
g = d.groupby("thinking_type")
t = pd.DataFrame({
    "n": g.size(),
    "baseline": g.apply(lambda x: 100 * x.plain_minmax.mean(), include_groups=False),
    "mt_bench": g.apply(lambda x: (x.dataset_id == "mt_bench").mean(), include_groups=False),
    "math": g.apply(lambda x: (x.dataset_id == "chat_math500").mean(), include_groups=False),
    "second_turn": g.apply(lambda x: x.second_turn.notna().mean(), include_groups=False),
}).reindex(ORDER)
t["level"] = [i.split("-")[0] for i in t.index]
t["target"] = [i.split("-")[1] for i in t.index]


def cv(a, b):
    """Cramér's V（两个二/三分类变量）。"""
    ct = pd.crosstab(pd.Series(a).values, pd.Series(b).values).values.astype(float)
    n = ct.sum()
    exp = ct.sum(1, keepdims=True) @ ct.sum(0, keepdims=True) / n
    chi2 = ((ct - exp) ** 2 / np.where(exp == 0, np.nan, exp)).sum()
    k = min(ct.shape) - 1
    return float(np.sqrt((chi2 / n) / k)) if k else np.nan


cands = {
    "A headroom (baseline<=70)": (t.baseline <= 70).astype(str).values,
    "B 承接上一轮 (mt_bench>=25%)": (t.mt_bench >= 0.25).astype(str).values,
    "C 收敛/发散 (target!=E)": (t.target != "E").astype(str).values,
    "D 精确判分 (math>=40%)": (t.math >= 0.40).astype(str).values,
}
print(t.round(2).to_string())
print()
print("%-30s %-16s %-8s %-8s" % ("candidate", "split", "V|level", "V|target"))
for k, v in cands.items():
    s = pd.Series(v).value_counts().to_dict()
    print("%-30s %-16s %-8.2f %-8.2f" % (k, s, cv(v, t.level), cv(v, t.target)))
print()
print("候选 B 的逐型标记：", {i: ("承接" if m >= 0.25 else "从零") for i, m in zip(t.index, t.mt_bench)})
