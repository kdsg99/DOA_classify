# -*- coding: utf-8 -*-
import sys

sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd                                             # noqa: E402

pd.set_option("display.width", 220)
d = pd.read_csv(r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\data\rows_v2.csv")
d["dpp"] = 100 * d.delta
d["p"] = 100 * d.plain_minmax
g = d[(d.thinking_type == "L1-F")][["strategy", "dataset_id", "task_id", "model", "p", "dpp"]]
print(g.sort_values(["strategy", "dataset_id"]).to_string(index=False))
print()
print("MISLEADING L1-F 行数:", len(d[(d.strategy == "MISLEADING") & (d.thinking_type == "L1-F")]))
print(d[(d.strategy == "MISLEADING") & (d.thinking_type == "L1-F")][["dataset_id", "task_id", "p", "dpp"]].to_string(index=False))
