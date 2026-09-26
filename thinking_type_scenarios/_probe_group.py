# -*- coding: utf-8 -*-
import sys
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
d = pd.read_csv(r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\data\rows_v2.csv")
for c in ("primary_group", "primary_tag", "secondary_tags", "target", "shift_direction", "set"):
    print("==", c, "nunique", d[c].nunique(dropna=False))
    vc = d[c].value_counts(dropna=False)
    print(vc.head(15).to_string())
    print()
print("primary_group x thinking_type:")
print(pd.crosstab(d.primary_group, d.thinking_type).to_string())
