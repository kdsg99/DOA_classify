# -*- coding: utf-8 -*-
import sys

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np                                              # noqa: E402
from PIL import Image                                           # noqa: E402

D = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios\taxonomy_search\figs"
for f in ["figA_spec.png", "figB_taxonomy.png"]:
    im = Image.open(D + "\\" + f).convert("L")
    a = np.asarray(im)
    h, w = a.shape
    print("%-18s %s ink=%.3f cols=%s" % (f, im.size, (a < 235).mean(),
                                         [round((a[:, i * w // 6:(i + 1) * w // 6] < 235).mean() * 100)
                                          for i in range(6)]))
