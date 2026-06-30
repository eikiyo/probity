# Probity — Benchmark Results

Accuracy = % correct vs a human-validated answer extracted from the source document. Reliability = % run-to-run agreement at temperature 0.7 (label-free). They are reported separately and never averaged.

Primary runners: **gemma4:12b** (local, zero egress) and **deepseek-v4-flash**. Frontier models are sampled occasionally, not on every leaf.

---

## Test 1.3.2 — Preferred-stock liquidation participation

**Corpus:** 13 real SEC-filed charter clauses, human-validated answers (8 non-participating / 3 participating / 2 capped). Majority-class baseline (always guess non-participating) = **62%**.

### Headline (accuracy vs validated answer · reliability = run-to-run consistency)

| Model | Accuracy (majority vote) | Accuracy (strict, all 5 runs) | Reliability | Measurable |
|---|---|---|---|---|
| `gemma4:12b` | **69%** | 69% | 100% | 13/13 |
| `deepseek-v4-flash` | **69%** | 69% | 100% | 13/13 |

### Accuracy by class

| Model | non-participating | participating | capped |
|---|---|---|---|
| `gemma4:12b` | 6/8 | 1/3 | 2/2 |
| `deepseek-v4-flash` | 6/8 | 1/3 | 2/2 |

### Hard-item spotlight (the traps)

| Item | True | `gemma4:12b` | `deepseek-v4-flash` |
|---|---|---|---|
| Pfenex Inc. | non-participating | ✗ (capped) | ✗ (capped) |
| BioAccelerate Holdings | non-participating | ✓ (non-participating) | ✓ (non-participating) |
| Entercom Communication | non-participating | ✓ (non-participating) | ✓ (non-participating) |
| IESI Corp | participating | ✓ (participating) | ✓ (participating) |

---

## What this round shows

- **Reliability is not accuracy — demonstrated on real data.** Both models answered identically
  across all 5 runs of every item (100% reliability) yet were wrong on 4 of 13 (69% accuracy).
  A model you can trust to be *consistent* is not a model you can trust to be *right*.
- **A 12B local model tied a frontier-class hosted model, exactly.** `gemma4:12b` and
  `deepseek-v4-flash` produced the same label on all 65 runs. Verified genuine (not a duplication
  bug): on a live re-run gemma emits ```json-fenced output and DeepSeek emits raw JSON — different
  models, same answers.
- **Shared blind spot = participating preferred.** Both got only 1/3 participating clauses right,
  misreading the "preference THEN also share with common" structure as *capped*.
- **A naming trap fooled both.** Pfenex's "Maximum Participation Amount" lured both models to
  *capped*, though its greater-of structure is non-participating.
- **A clean greater-of was misread.** Zoom's textbook non-participating clause was called
  *participating* by both models.

The errors are systematic and shared across two very different models — evidence of a common
misconception about preferred-stock liquidation, not random sampling noise. This is exactly the
reliable-but-wrong failure a finance agent would propagate silently.

## Reproduce

```bash
cd leaves/participation_type
python3 source.py     # re-fetch the real SEC charter clauses
python3 run.py        # run gemma + DeepSeek, score
python3 ../../results/render.py
```

Corpus: real SEC EDGAR charter exhibits; answers human-validated from each clause's own legal text
(see `leaves/participation_type/oracle.jsonl`, with the validating quote per item).

