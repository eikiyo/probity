"""Terminal demo: replays 20 REAL model runs (gemma3:1b) against the same clause,
same prompt, temp 0.7 -- recorded verbatim in leaves/pre_vs_post_money/runs_gemma3-1b.jsonl.
No live model call here; this is a deterministic replay for the README GIF.
"""
import sys
import time

ANSWERS = [
    "post-money", "post-money", "post-money", "pre-money", "post-money",
    "pre-money", "pre-money", "post-money", "pre-money", "post-money",
    "post-money", "pre-money", "pre-money", "pre-initial", "post-money",
    "post-money", "post-money", "post-money", "post-money", "post-money",
]


def slow_print(text, delay=0.012):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def main():
    slow_print("$ probity demo -- same clause, same model, 20 runs, temp 0.7\n", 0.02)
    time.sleep(0.4)
    slow_print("Q: this term sheet cites an $8,000,000 valuation -- is it PRE-money or POST-money?\n", 0.015)
    time.sleep(0.5)

    baseline = ANSWERS[0]
    flips = 0
    for i, ans in enumerate(ANSWERS, start=1):
        flag = ""
        if ans != baseline:
            flips += 1
            flag = "  <- FLIPPED"
        print(f"  run {i:02d}: {ans}{flag}")
        time.sleep(0.09)

    time.sleep(0.5)
    print()
    slow_print("Same clause. Same model. 20 identical prompts.", 0.018)
    slow_print(f"{len(set(ANSWERS))} different answers on a binary question.", 0.018)
    time.sleep(0.3)
    print()
    slow_print(f"  Wobble: {100 * flips / len(ANSWERS):.0f}%", 0.03)
    time.sleep(0.6)
    print()
    slow_print("A model that flips pre-money vs post-money cannot price a round.", 0.018)
    slow_print("This is why Probity exists.", 0.02)
    time.sleep(1.0)


if __name__ == "__main__":
    main()
