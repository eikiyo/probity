# Probity — reviewer data dump

Everything behind the paper's numbers, in open formats, with a verifier that recomputes those
numbers from the raw records using its own independent implementation.

## Verify it yourself (no dependencies, stdlib only)

```bash
sha256sum -c CHECKSUMS.sha256          # the dump is the dump that was reviewed
python3 verify_dump.py --dump . --expect expected_numbers.json
```

That recomputes wobble and accuracy for every model from `runs.jsonl.gz` + `oracle.jsonl.gz` and
asserts they match the published figures. It imports nothing from the benchmark — if it agreed
with us only because it reused our code, it would prove nothing.

## Files

| File | What |
|---|---|
| `runs.jsonl.gz` | One row per model call. The rawest artifact held. |
| `oracle.jsonl.gz` | The 470 human-validated answers, with the quote that validates each. |
| `prompts.jsonl.gz` | The exact prompt sent for every item, reconstructed from each leaf's own builder. |
| `scored.jsonl.gz` | Per (leaf, model, arm) scored summary as the pipeline computed it. |
| `manifests.jsonl.gz` | Reproducibility metadata: provider model id, routing, requested temperature. |
| `coverage.csv` | Calls OWED vs RECORDED per cell. Owed is items x 20 from the oracle — the spec. |
| `expected_numbers.json` | The published figures, for `--expect`. |
| `INDEX.json` | Row counts per file. |
| `CHECKSUMS.sha256` | sha256 of every file above. |

## Key fields in `runs.jsonl.gz`

`leaf` · `field` · `family` · `model_label` · `arm` · `temperature` · `instance_idx` · `run_idx` ·
`item_id` · `parsed` (values extracted from the response) · `normalized` (those values coerced to
the field's type — **this is what scoring compares**) · `error` (provider/network failure, if any) ·
`raw_output` (see limitation 1).

An item is **measured** for a model when at least one of its 20 runs produced a non-null
`normalized` value. **Wobble** is the share of measured items where the model gave more than one
distinct normalized answer. **Accuracy** is the share whose majority answer equals
`truth_canonical`. They are reported separately and never averaged.

## Limitations — read these before drawing conclusions

1. **Raw response text is retained only for calls that failed to parse**, truncated to 200
   characters. For a call that parsed successfully the harness stored `parsed` and `normalized`
   and discarded the response body. This applies to **both** temperature arms. It means a
   reviewer can audit our parsing on the cases where parsing is contestable, but cannot
   re-parse a successful response from scratch. This is a property of how the sweeps were
   recorded and cannot be reconstructed after the fact.
2. **`truth_canonical` is shipped alongside the raw oracle value** because scoring compares
   canonicalised forms on both sides (a numeric answer written `"100000000"` in the oracle must
   match a parsed `100000000`). Both are present so the canonicalisation itself is auditable.
3. **Per-call HTTP retries are not counted.** The client retries transient failures in process
   without persisting an attempt counter. Retried calls are billed and included in cost figures
   but are not separately countable here.
4. **`t07_legacy` and `t01` were measured ~25 days apart.** Provider-side model drift is not
   controlled for and is a known confound, disclosed rather than corrected.
5. **Local models (`gemma3-1b`, `gemma3-1b-qat`) in `t07_legacy` ran on different hardware**
   than the hosted models. Where a local model is compared across arms, both arms come from the
   same machine; the legacy local numbers are never paired against a different-runtime arm.
