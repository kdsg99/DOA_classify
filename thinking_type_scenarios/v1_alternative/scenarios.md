# Re-ask strategy × thinking-type scenarios

Values are score changes in pp (re-ask − plain). `balanced` = difficulty-adjusted and
re-averaged with equal weight per evaluation family (independent of sample sizes).

## Layer means (raw)

| Strategy | Metacognitive | Structural | Execution | Overall |
|---|---|---|---|---|
| PRESSURE | +19.9 | +2.3 | +0.3 | +9.1 |
| CRITICAL | +8.6 | -11.9 | -21.4 | -5.8 |
| ENCOURAGE | -1.6 | -20.8 | -29.1 | -14.9 |
| MISLEADING | -15.5 | -22.2 | -34.9 | -22.6 |
| HEURISTIC | -28.4 | -28.1 | -32.1 | -29.2 |

## Layer means (difficulty-adjusted)

| Strategy | Metacognitive | Structural | Execution | Overall |
|---|---|---|---|---|
| PRESSURE | +14.8 | -0.1 | -0.9 | +5.9 |
| CRITICAL | +14.2 | +6.3 | +0.9 | +8.2 |
| ENCOURAGE | +11.9 | +3.6 | +0.9 | +6.4 |
| MISLEADING | +5.3 | +5.4 | -1.9 | +3.6 |
| HEURISTIC | +8.3 | +3.7 | +3.1 | +5.5 |

## Layer means (balanced)

| Strategy | Metacognitive | Structural | Execution | Overall |
|---|---|---|---|---|
| PRESSURE | +14.7 | +4.0 | -1.0 | +7.2 |
| CRITICAL | +15.4 | +9.9 | +2.2 | +10.3 |
| ENCOURAGE | +13.2 | +6.0 | +11.2 | +10.3 |
| MISLEADING | +8.7 | +7.2 | +2.5 | +6.6 |
| HEURISTIC | +8.0 | +7.7 | +14.7 | +9.6 |

## Per-strategy reading (balanced, with the raw value for reference)

### PRESSURE

Helps:
  - Trajectory sensitive [Metacognitive] — +25.3 pp balanced (raw +11.8, n=2, families=2) → keep the reasoning path / step order intact
  - Strict verification [Metacognitive] — +25.3 pp balanced (raw +50.0, n=1, families=1) → fact-checking and correctness validation
  - Reviewable repair [Metacognitive] — +14.2 pp balanced (raw +30.6, n=4, families=2) → review / critique / give feedback on someone else's answer

Hurts:
  - Local repair [Execution] — -5.3 pp balanced (raw +8.0, n=14, families=4) → patch a concrete error / bug / hallucination
  - Execution-limited [Execution] — -4.2 pp balanced (raw -10.2, n=32, families=6) → simple but labour-heavy routines (arithmetic, sudoku, lookup chains)
  - Full-reasoning dependent [Structural] — -1.3 pp balanced (raw +1.3, n=166, families=6) → multi-step maths / physics / logic proofs

Most family-dependent cell: Style preserving (leave-one-family-out spread 14.8 pp)

### CRITICAL

Helps:
  - Long-context fidelity [Metacognitive] — +31.0 pp balanced (raw +7.1, n=17, families=4) → long documents, summarise while keeping consistency
  - Strict verification [Metacognitive] — +27.0 pp balanced (raw +65.6, n=2, families=2) → fact-checking and correctness validation
  - Routine recognition [Structural] — +23.1 pp balanced (raw +1.1, n=42, families=5) → classification, matching, pattern recognition

Hurts:
  - Reviewable repair [Metacognitive] — -7.6 pp balanced (raw -9.0, n=6, families=2) → review / critique / give feedback on someone else's answer
  - Execution-limited [Execution] — -7.1 pp balanced (raw -48.5, n=50, families=6) → simple but labour-heavy routines (arithmetic, sudoku, lookup chains)
  - Full-reasoning dependent [Structural] — -0.3 pp balanced (raw -30.6, n=222, families=6) → multi-step maths / physics / logic proofs

Most family-dependent cell: Execution-limited (leave-one-family-out spread 13.5 pp)

### ENCOURAGE

Helps:
  - Long-context fidelity [Metacognitive] — +31.7 pp balanced (raw -3.1, n=21, families=4) → long documents, summarise while keeping consistency
  - Trajectory sensitive [Metacognitive] — +21.3 pp balanced (raw -17.4, n=6, families=2) → keep the reasoning path / step order intact
  - Expression expansion [Execution] — +19.7 pp balanced (raw -11.3, n=80, families=5) → write long-form, creative or expansive text

Hurts:
  - Reviewable repair [Metacognitive] — -12.5 pp balanced (raw -12.5, n=6, families=2) → review / critique / give feedback on someone else's answer
  - Format preserving [Structural] — -5.7 pp balanced (raw -21.4, n=25, families=5) → strict output formats (JSON, CSV, table, LaTeX)
  - Local repair [Execution] — +0.7 pp balanced (raw -15.5, n=14, families=5) → patch a concrete error / bug / hallucination

Most family-dependent cell: Style preserving (leave-one-family-out spread 25.8 pp)

### MISLEADING

Helps:
  - Long-context fidelity [Metacognitive] — +35.8 pp balanced (raw -8.1, n=22, families=4) → long documents, summarise while keeping consistency
  - Plain-answer fragile [Metacognitive] — +16.9 pp balanced (raw -14.8, n=27, families=4) → short factual answers without reasoning
  - Routine recognition [Structural] — +15.8 pp balanced (raw -9.5, n=44, families=5) → classification, matching, pattern recognition

Hurts:
  - Execution-limited [Execution] — -9.5 pp balanced (raw -69.3, n=59, families=6) → simple but labour-heavy routines (arithmetic, sudoku, lookup chains)
  - Reviewable repair [Metacognitive] — -9.4 pp balanced (raw -20.0, n=5, families=2) → review / critique / give feedback on someone else's answer
  - Strict verification [Metacognitive] — -6.5 pp balanced (raw +13.5, n=2, families=2) → fact-checking and correctness validation

Most family-dependent cell: Style preserving (leave-one-family-out spread 17.9 pp)

### HEURISTIC

Helps:
  - Long-context fidelity [Metacognitive] — +33.6 pp balanced (raw -6.1, n=20, families=4) → long documents, summarise while keeping consistency
  - Expression expansion [Execution] — +26.3 pp balanced (raw -14.5, n=90, families=5) → write long-form, creative or expansive text
  - Trajectory sensitive [Metacognitive] — +19.5 pp balanced (raw -31.9, n=4, families=2) → keep the reasoning path / step order intact

Hurts:
  - Strict verification [Metacognitive] — -17.0 pp balanced (raw -75.0, n=2, families=1) → fact-checking and correctness validation
  - Reviewable repair [Metacognitive] — -4.5 pp balanced (raw -13.0, n=6, families=2) → review / critique / give feedback on someone else's answer
  - Local repair [Execution] — +1.6 pp balanced (raw -13.4, n=16, families=5) → patch a concrete error / bug / hallucination

Most family-dependent cell: Local repair (leave-one-family-out spread 17.5 pp)
