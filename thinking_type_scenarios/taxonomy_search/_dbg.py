# -*- coding: utf-8 -*-
import sys

sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd                                             # noqa: E402
sys.path.insert(0, r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\taxonomy_search")
import step1_screen as S                                        # noqa: E402

piv, feat = S.load()
print("feat shape", feat.shape)
for c in ["dataset_id", "category", "primary_tag", "primary_group", "skill0", "domain0", "level_label",
          "thinking_type", "target", "primary"]:
    s = feat[c].astype(str)
    print("%-14s nuniq=%3d  head=%s" % (c, s.nunique(), str(s.value_counts().head(4).to_dict())[:120]))
print()
lab = pd.Series(feat.dataset_id, index=feat.index).astype(str)
print("lab nuniq", lab.nunique(), lab.value_counts().head().to_dict())
C = S.contrasts(piv, S.FOCAL)
print("C shape", C.shape, "index head", list(C.index[:3]))
V, N = S.v_matrix(C, lab, S.FOCAL)
print("V shape", V.shape)
print(V.head(8).round(2).to_string())
