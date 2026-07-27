"""
Kaggle kernel - Probity TRACK C: the two LOCAL models across all 60 leaves, off-laptop on a T4.

WHY THIS EXISTS: gemma3-1b and gemma3-1b-qat were measured for the published 0.7 arm on Eikiyo's
Mac. Running only the 0.1 arm on Kaggle would change the RUNTIME between the two halves of a
paired comparison, so temperature would no longer be the only variable. This kernel therefore runs
BOTH arms on the SAME machine in the SAME session (Plan B), and the pair reported for local models
is Kaggle-t07 vs Kaggle-t01. The Mac-measured 0.7 numbers stay published but are never paired
against a Kaggle 0.1 number.

PARITY BY CONSTRUCTION: this does NOT reimplement scoring. It unpacks the real engine and calls
runner.run_leaf() -- the identical code path the hosted tracks use -- so prompts, parsing, scoring,
checkpoint format and the coverage assert are the same objects, not lookalikes. The only thing that
differs is the client (OllamaClient) and where it runs.

Fail closed + observable (Sec 0.7): every stage logs a reason, beacons progress (Kaggle commits
output only at terminal state), and exits non-zero on failure.
"""
import os, sys, json, time, subprocess, glob, urllib.request

MODELS = [("gemma3-1b", "gemma3:1b"), ("gemma3-1b-qat", "gemma3:1b-it-qat")]
ARMS = [0.7, 0.1]              # BOTH arms, same machine, same session -- the whole point
N_RUNS, WORKERS = 20, 4
SMOKE = os.environ.get("PROBITY_SMOKE") == "1"

OUT = "/kaggle/working/arm_result.json"
NTFY = "https://ntfy.sh/probity-arm-kage-x7q2"
RES = {"models": [m[0] for m in MODELS], "arms": ARMS, "n_runs": N_RUNS,
       "smoke": SMOKE, "cells": {}, "notes": [], "status": "FAIL"}


def log(m): print(f"[arm] {m}", flush=True)
def save(): open(OUT, "w").write(json.dumps(RES, indent=2))


def beacon(msg):
    try:
        urllib.request.urlopen(urllib.request.Request(
            NTFY, data=str(msg).encode()[:900], method="POST"), timeout=10).read()
    except Exception as e:
        log(f"beacon failed (non-fatal): {e}")


def sh(cmd, timeout=900):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout or "")[-400:], (r.stderr or "")[-400:]


def die(msg):
    RES["notes"].append(msg); beacon(f"FAIL {msg}"); save(); log(f"FAIL {msg}"); sys.exit(1)


def install_ollama():
    """Reuses the proven .tar.zst path from kaggle-eval/eval.py (validated 2026-07-05)."""
    rc, o, e = sh("curl -fsSL https://ollama.com/download/ollama-linux-amd64.tar.zst -o /tmp/o.tar.zst && "
                  "( tar --zstd -xf /tmp/o.tar.zst -C /usr/local "
                  "|| ( (command -v zstd >/dev/null || (apt-get -qq update && apt-get -qq install -y zstd)) && "
                  "zstd -d -f /tmp/o.tar.zst -o /tmp/o.tar && tar -xf /tmp/o.tar -C /usr/local ) )", timeout=900)
    os.environ["PATH"] = "/usr/local/bin:" + os.environ.get("PATH", "")
    if not os.path.exists("/usr/local/bin/ollama"):
        die(f"ollama binary missing after install rc={rc} err={e[-200:]}")
    subprocess.Popen("OLLAMA_NUM_PARALLEL=4 /usr/local/bin/ollama serve "
                     "> /kaggle/working/ollama.log 2>&1", shell=True)
    for _ in range(45):
        if sh("curl -s http://127.0.0.1:11434/api/version", timeout=10)[0] == 0:
            return
        time.sleep(2)
    tail = open("/kaggle/working/ollama.log").read()[-300:] if os.path.exists("/kaggle/working/ollama.log") else "none"
    die(f"ollama not ready after 90s; log: {tail}")


def unpack_harness():
    tgz = glob.glob("/kaggle/input/**/probity-arm-harness.tgz", recursive=True)
    if not tgz:
        die(f"harness tgz not found; /kaggle/input={os.listdir('/kaggle/input')}")
    sh(f"mkdir -p /kaggle/working/probity && tar xzf {tgz[0]} -C /kaggle/working/probity", timeout=300)
    cand = glob.glob("/kaggle/working/probity/**/engine/runner.py", recursive=True)
    if not cand:
        die("engine/runner.py not found after extract")
    root = os.path.dirname(os.path.dirname(cand[0]))
    sys.path.insert(0, f"{root}/engine")
    return root


def main():
    t0 = time.time()
    log("installing ollama...")
    install_ollama()
    _, smi, _ = sh("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader")
    beacon(f"START track-C gpu={smi.strip()[:60]} models={[m[0] for m in MODELS]} arms={ARMS}")

    root = unpack_harness()
    import runner, coverage                                    # noqa: E402
    from models import OllamaClient                            # noqa: E402
    leaves = sorted(d for d in os.listdir(f"{root}/leaves")
                    if os.path.exists(f"{root}/leaves/{d}/task.py"))
    if SMOKE:
        leaves = leaves[:2]
    log(f"{len(leaves)} leaves, root={root}")

    for label, ref in MODELS:
        rc, _, e = sh(f"ollama pull {ref}", timeout=2400)
        if rc != 0:
            die(f"pull failed {ref}: {e[-160:]}")
        beacon(f"pulled {ref}")

    from pathlib import Path
    for temp in ARMS:
        for label, ref in MODELS:
            # ONE model set, built the same way runner's own helpers build theirs. ollama_model is
            # passed so run_model unloads it between arms and the 1B pair never share VRAM.
            mset = [(label, ref, (lambda r=ref: OllamaClient(r)))]
            for i, leaf in enumerate(leaves, 1):
                d = Path(root) / "leaves" / leaf
                try:
                    runner.run_leaf(d, model_set=mset, only=label,
                                    temperature=temp, max_workers=WORKERS)
                except Exception as ex:
                    RES["notes"].append(f"{leaf}/{label}@{temp}: {ex}")
                    log(f"ERROR {leaf}/{label}@{temp}: {ex}")
                cell = coverage.cell_status(d, label, N_RUNS, coverage.artifact_suffix(temp))
                RES["cells"][f"{label}@{temp}/{leaf}"] = cell
                if i % 10 == 0 or i == len(leaves):
                    done = sum(1 for c in RES["cells"].values() if c["complete"])
                    beacon(f"{label}@{temp} {i}/{len(leaves)} leaves | {done} cells full | "
                           f"{int(time.time()-t0)}s")
                    save()

    # Fail closed on coverage, exactly like the hosted sweep does.
    holes = [k for k, c in RES["cells"].items() if not c["complete"]]
    RES["recorded"] = sum(c["recorded"] for c in RES["cells"].values())
    RES["owed"] = sum(c["expected"] for c in RES["cells"].values())
    RES["holes"] = holes
    RES["seconds"] = round(time.time() - t0, 1)
    # Ship the checkpoints back: /kaggle/working is the only thing that leaves the kernel.
    sh(f"cd {root} && tar czf /kaggle/working/arm-results.tgz "
       f"$(find leaves -name 'runs_*.jsonl' -o -name 'scored*.json' -o -name 'manifest_*.json' "
       f"| tr '\\n' ' ')", timeout=600)
    if holes:
        RES["status"] = "INCOMPLETE"
        save(); beacon(f"INCOMPLETE {len(holes)} cells short, {RES['recorded']}/{RES['owed']}")
        log(f"INCOMPLETE: {len(holes)} cells short"); sys.exit(1)
    RES["status"] = "OK"
    save(); beacon(f"DONE {RES['recorded']}/{RES['owed']} calls in {RES['seconds']}s")
    log("TRACK C DONE")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        import traceback
        die(f"unhandled: {traceback.format_exc()[-500:]}")
