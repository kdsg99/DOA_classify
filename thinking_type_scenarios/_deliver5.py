# -*- coding: utf-8 -*-
"""重发交付：更新 deliver/ 与 figs/ 的副本，追加 command_record。"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")
H = r"C:\Users\kl001\.nanobot\DOA\thinking_type_scenarios"
F = r"C:\Users\kl001\.nanobot\figs"
DEL = r"C:\Users\kl001\.nanobot\deliver"
for d in (F, DEL):
    os.makedirs(d, exist_ok=True)
for src, dst in [("fig1_raw.png", "tt6_fig1_raw_3dim.png"),
                 ("fig2_difficulty.png", "tt6_fig2_difficulty_3dim.png"),
                 ("fig3_balanced.png", "tt6_fig3_balanced_3dim.png"),
                 ("fig2_difficulty_levels.png", "tt6_fig2L_difficulty_levels_3dim.png")]:
    shutil.copy2(os.path.join(H, "figs_tt6", src), os.path.join(F, dst))
    print("figs\\%s" % dst)
for src, dst in [("figs_tt6\\fig2_difficulty.png", "tt6_fig2_difficulty.png"),
                 ("figs_tt6\\fig1_raw.png", "tt6_fig1_raw.png"),
                 ("figs_tt6\\fig3_balanced.png", "tt6_fig3_balanced.png"),
                 ("figs_tt6\\fig2_difficulty_levels.png", "tt6_fig2L_levels.png"),
                 ("DIFFICULTY_CORRECTION.md", "DIFFICULTY_CORRECTION.md"),
                 ("make_figs_tt6.py", "make_figs_tt6.py"),
                 ("tt3_analysis.py", "tt3_analysis.py"),
                 ("taxonomy_v2.py", "taxonomy_v2.py"),
                 ("_sens_mix.py", "_sens_mix.py")]:
    shutil.copy2(os.path.join(H, src), os.path.join(DEL, dst))
    print("deliver\\%-32s %6.0f KB" % (dst, os.path.getsize(os.path.join(DEL, dst)) / 1024))

p = r"C:\Users\kl001\.nanobot\command_record.md"
mark = "### 2026-09-22 增补十：回信附件用 [[attach:]] 标记 + mail_bridge 补非图片 MIME + 图例放大"
e = """

### 2026-09-22 增补十：回信附件用 [[attach:]] 标记 + mail_bridge 补非图片 MIME + 图例放大
- 故障：上一次回信只附上了 4 张 png，DIFFICULTY_CORRECTION.md 与 4 个 .py 没附上。原因不在 bridge，
  而是回复正文只把图片写成 [[inline: 路径]] 标记、md/py 只写成纯文本"附件：路径"清单，未被解析。
  规则：非图片附件必须逐行写 [[attach: 路径]]，图片写 [[inline: 路径]]（会同时作为附件）。
- mail_bridge.py 增强：新增 FILE_MIME 映射（.md→text/markdown、.py→text/x-python、.txt/.csv/.json/
  .pdf/.zip/.xlsx/.docx），非图片附件按真实 MIME 走 base64，未列出的扩展名仍按
  application/octet-stream，避免 Outlook 侧类型不明。
- 自检：extract_outbound_attachments 对 attach/inline 混排、文件不存在（忽略并记日志）均正确；
  bridge 导入无副作用。
- 图例按用户要求改回 tt5 的格式（放大）：标题行 + 三级层级行（L1 Execution — colour 等）+
  四行对象行（— pattern）+ 两行虚实行（room left ≥30pp — solid / almost solved <30pp — hollow），
  色块 0.055×0.030、行距 0.052、字号 8.4（原先缩到 0.033×0.024、字号 8.0，被用户判为太小）。
- 四张 tt6 图已重新生成（figs_tt6\\、figs\\tt6_*_3dim.png、deliver\\）。
"""
t = open(p, encoding="utf-8").read()
if mark in t:
    print("record 已存在，跳过")
else:
    open(p, "a", encoding="utf-8").write(e)
    print("record 已追加，%.1f KB" % (os.path.getsize(p) / 1024))
