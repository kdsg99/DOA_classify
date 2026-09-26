# Three-Dimension Values per Thinking Type (Figure 2 companion table)

*12 thinking types x three dimensions (operation level / target of intervention / starting state), with
measured values, sample sizes and a one-line cognitive-demand description. Design rationale in
`fig2_design.md`; strategy-side conclusions in `fig2_strategy_findings.md`.*

---

## Table 1 Main table: three-dimension values of the 12 types

In the `dim3` column the parenthesised number is the continuation share `c_t` (≥ 30 % = continuation);
`baseline p̄` is the type's mean score under the no-strategy condition (0–100); `n` is the number of task
rows for that type (summed over strategies).

| type | Name (EN) | Name (ZH) | dim1 operation level | dim2 target | dim3 starting state | baseline p̄ | n |
|---|---|---|---|---|---|---|---|
| L1-K | Knowledge Retrieval | 知识提取 | L1 Execution | K Knowledge | from scratch (0.24) | 67.4 | 249 |
| L1-R | Direct Computation | 直接求解 | L1 Execution | R Reasoning | continuation (0.30) | 85.8 | 680 |
| L1-E | Content Generation | 内容生成 | L1 Execution | E Expression | continuation (0.49) | 74.7 | 179 |
| L1-F | Format Transformation | 格式转换 | L1 Execution | F Format | from scratch (0.00) | 92.0 | 12 |
| L2-K | Knowledge Synthesis | 知识整合 | L2 Structure | K Knowledge | continuation (0.38) | 77.7 | 281 |
| L2-R | Multi-Step Derivation | 多步推理 | L2 Structure | R Reasoning | from scratch (0.05) | 68.7 | 643 |
| L2-E | Discourse Organization | 篇章组织 | L2 Structure | E Expression | from scratch (0.26) | 67.7 | 170 |
| L2-F | Structured Output | 结构化输出 | L2 Structure | F Format | continuation (0.68) | 71.6 | 96 |
| L3-K | Factual Verification | 事实验证 | L3 Metacognition | K Knowledge | from scratch (0.00) | 55.2 | 112 |
| L3-R | Process Control | 过程控制 | L3 Metacognition | R Reasoning | continuation (0.34) | 65.6 | 218 |
| L3-E | Style & Persona Fidelity | 风格保持 | L3 Metacognition | E Expression | continuation (0.57) | 69.9 | 129 |
| L3-F | Constraint Check & Repair | 约束校验修复 | L3 Metacognition | F Format | from scratch (0.28) | 77.7 | 32 |

## Table 2 What thinking the three dimensions jointly demand (one line per type)

Template: **(level) do what + (target) on what + (starting state) starting from where**.

| type | Cognitive demand | Characteristic failure |
|---|---|---|
| L1-K | From scratch, retrieve the fact/knowledge point the question targets (single step) | cannot retrieve it, retrieves the wrong thing |
| L1-R | Do one direct computation on the given problem or on the previous turn's result (single step; the high baseline of 85.8 says most items are already solved) | computes wrong, misreads the conditions |
| L1-E | Directly generate / rewrite one passage on top of an existing output (tone, wording, length) | drifts off topic, wrong register |
| L1-F | From scratch, convert given content into another format; every hard constraint must be hit | misses items, violates the format (thin cell, n = 2–3; reference only) |
| L2-K | On existing material, synthesise several sources into a coherent answer (retrieve, then organise) | lists without synthesising, leaves source conflicts unresolved |
| L2-R | Chain a multi-step derivation from scratch (no existing chain to continue); one wrong step ruins everything | errors mid-way, skips steps |
| L2-E | Build a discourse structure from scratch: sections, order, connectives, level of detail | loose structure, muddled hierarchy |
| L2-F | Continue existing content by rearranging it into a specified structure (table / schema / template) | structure does not hold, fields missing |
| L3-K | From scratch, verify an existing claim or the model's own just-produced conclusion (needs an external anchor) | does not check, checks in the wrong direction, follows the error |
| L3-R | Continue an ongoing process and control/repair it (spot the deviation and correct it) | does not spot the deviation, edits what should not be edited |
| L3-E | Continue an existing text while keeping style/persona consistent (edits must stay restrained) | style drift, edits make it less faithful |
| L3-F | From scratch, check every item on the constraint list and repair it (constraint satisfaction is the only criterion) | misses items, fixing one breaks another |

## Table 3 Distribution check: the three dimensions are mutually orthogonal

- **Dimension 1 (level)**: 4 types each on L1 / L2 / L3.
- **Dimension 2 (target)**: 3 types each on K / R / E / F.
- **Dimension 3 (starting state)**: 6 continuation / 6 from scratch, **exactly 2 : 2 within every level**
  and 1–2 : 2–1 within every target — i.e. the third dimension does not reintroduce any imbalance on
  level or target.

| dim1 \ dim3 | continuation | from scratch |
|---|---|---|
| L1 Execution | L1-R, L1-E | L1-K, L1-F |
| L2 Structure | L2-K, L2-F | L2-R, L2-E |
| L3 Metacognition | L3-R, L3-E | L3-K, L3-F |

| dim2 \ dim3 | continuation | from scratch |
|---|---|---|
| K Knowledge | L2-K | L1-K, L3-K |
| R Reasoning | L1-R, L3-R | L2-R |
| E Expression | L1-E, L3-E | L2-E |
| F Format | L2-F | L1-F, L3-F |

Orthogonality check (Cramér's V, 0 = independent): starting state vs level = **0.00**; starting state vs
target = 0.33. For comparison: headroom vs level = 0.41 and vs target = 0.58 (hence not used as the third
dimension).

## Table 4 Sample-size check (rows per cell, per strategy)

| type | n (all strategies) | per-cell n range | thin flags |
|---|---|---|---|
| L1-K | 249 | 45–54 | — |
| L1-R | 680 | 70–204 | — |
| L1-E | 179 | 25–41 | — |
| L1-F | 12 | 2–3 | ⚠ thin for every strategy |
| L2-K | 281 | 48–63 | — |
| L2-R | 643 | 82–176 | — |
| L2-E | 170 | 29–37 | — |
| L2-F | 96 | 16–21 | — |
| L3-K | 112 | 20–25 | — |
| L3-R | 218 | 38–48 | — |
| L3-E | 129 | 22–29 | — |
| L3-F | 32 | 5–7 | ⚠ thin for every strategy |

Note: `n < 15` is treated as thin (red `n=` and a lighter bar in the figure). `L1-F` and `L3-F` are thin
in every strategy, so any statement about these two types can only be directional.

## Appendix: how to read this table off the figure

- Blue/green/red = dimension 1 of Table 1; none/diagonal/cross/backslash = dimension 2; solid vs pale
  dashed = dimension 3.
- The left y-axis lists `type ID + English name`, with a dashed line every 4 rows, matching the
  L1 / L2 / L3 blocks.
- The number at the end of a bar is that strategy's **relative** profile value for the type (`std_rel`,
  pp, difficulty-corrected and centred on the strategy's own 12 types).
- The absolute (uncentred) scale (`std`, `std_fam`) is in `out/cells_3dims.csv`.
