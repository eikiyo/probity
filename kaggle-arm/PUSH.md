# Track C — local models on Kaggle (STAGED, not pushed)

## Status: BLOCKED on network, not on work

`api.kaggle.com` and `www.kaggle.com` are unreachable from this machine's network
(DNS resolves to 34.54.168.202, TCP connect fails; OpenRouter on the same box returns 200).
Credentials are fine — `~/.kaggle/access_token` is present and was verified working 2026-07-05.
Everything below is ready to run the moment Kaggle is reachable.

## What this runs

Both LOCAL benchmark models across all 60 leaves, at BOTH temperatures, on one T4 in one session:

| | |
|---|---|
| Models | `gemma3:1b`, `gemma3:1b-it-qat` |
| Arms | 0.7 **and** 0.1 |
| Calls | 2 models x 2 arms x 9,400 = **37,600** |
| Cost | $0 (free T4 quota) |

## Why BOTH arms and not just 0.1

The published 0.7 numbers for these two models were measured on Eikiyo's Mac. Running only the
0.1 arm on a T4 would change the RUNTIME between the two halves of a paired comparison, so
temperature would stop being the only variable. Track C therefore measures both arms on the same
machine in the same session, and the local pair reported in the paper is Kaggle-0.7 vs Kaggle-0.1.
The Mac-measured 0.7 numbers stay published as the legacy arm but are never paired against a
Kaggle 0.1 number.

## Parity by construction

`arm_kernel.py` does NOT reimplement scoring. It unpacks the real engine and calls
`runner.run_leaf()` — the identical code path the hosted tracks use — so prompts, parsing, scoring,
checkpoint format and the coverage assert are the same objects, not lookalikes. Verified statically
against the live engine: `run_leaf` kwargs, `OllamaClient.generate(prompt, temperature)`,
`coverage.cell_status/artifact_suffix`, and that both labels match `preflight.LINEUP` exactly.

## Run it

```bash
cd kaggle-arm
./pack.sh                                            # -> probity-arm-harness.tgz (14M, 60 oracles)

# one-time: create the dataset
kaggle datasets init -p .
kaggle datasets create -p . -u                       # slug: seyedmosayebalam/probity-arm-harness
# thereafter:
kaggle datasets version -p . -m "arm harness" -d

kaggle kernels push -p .                             # slug: seyedmosayebalam/probity-arm-local
kaggle kernels status seyedmosayebalam/probity-arm-local
```

Live progress without waiting for the kernel to terminate (Kaggle commits output only at the end):

```bash
curl -s "https://ntfy.sh/probity-arm-kage-x7q2/json?poll=1" | tail -5
```

Smoke first (2 leaves instead of 60): set `PROBITY_SMOKE=1` in the kernel env, or edit `SMOKE`.

## Bring the results home

```bash
kaggle kernels output seyedmosayebalam/probity-arm-local -p /tmp/armout
tar xzf /tmp/armout/arm-results.tgz -C ~/probity        # restores runs_*/scored*/manifest_* into leaves/
python3 engine/backfill.py --temperature 0.1 --dry-run  # confirm 0 holes for the local labels
python3 results/render.py --temperature 0.1
```

## Fail-closed behaviour

- Any stage failure logs a reason, beacons it, and exits non-zero.
- A short cell sets `status: INCOMPLETE`, lists the holes, and exits 1 — a partial run can never
  read as done.
- Results tgz is written BEFORE the coverage assert, so even an incomplete run ships its data back
  and resumes rather than being re-billed in wall-clock.
