# Probity

**A reliability + accuracy benchmark for LLMs on real fundraising documents.**

Probity measures how trustworthy a language model is when it reads the legal and financial
documents that decide who owns what in a startup financing — term sheets, charters, SAFEs,
convertible notes, cap tables. It reports two numbers that are usually conflated and shouldn't be:

- **Accuracy** — does the model get the answer *right*, graded against a validated answer that a
  human extracted from the source document (not authored by an AI)?
- **Reliability** — does the model give the *same* answer when you ask it the same question five
  times at temperature 0.7? A model that is right once and wrong four times is not usable in a
  workflow that touches money.

These are scored separately and never averaged into one headline.

## Why the answers are trustworthy

Most LLM benchmarks in niche domains are built from synthetic data with synthetic answers. That has
a hidden flaw: if an AI writes both the question and the answer key, the answer key can be wrong in
exactly the ways the model under test is wrong. Probity avoids this with a strict **oracle layer**:

1. **Source a real document** that contains the ground truth in its own authoritative text — for
   example, a Certificate of Incorporation filed with the SEC that states, in legally precise
   language, whether its preferred stock is participating.
2. **A human separates the question from the answer.** The model sees only the clause (the question).
   The validated label, plus the exact quote that proves it, is stored in a separate oracle file the
   model never sees. Items whose answer cannot be determined with confidence are *excluded*, not guessed.
3. **Run only the question** through each model, N times, and score the majority answer against the
   validated label.

Synthetic instantiation is used only to *multiply* difficulty (varying numbers, off-market terms,
ambiguous phrasing) on top of a real, human-validated seed — never as the sole source of truth.

## The test map

Probity's full test backlog is a structured map of fundraising-reasoning capabilities
(`engine/registry.json`) — 67 atomic checks across priced equity, convertibles, cap-table math,
exit waterfalls, investor rights, founder equity, regulatory filings, and off-market risk flags.
Each check is built one at a time, to depth, against real sourced documents.

## Results

See [`results/RESULTS.md`](results/RESULTS.md) for the live benchmark table.

## Structure

```
engine/    the model-agnostic core: clients, run harness, normalizer, reliability+accuracy scorers
leaves/    one folder per test, each with its real-document corpus, its separated oracle, and its runner
results/   the living benchmark table
```

## Running a test

```bash
cd leaves/<test_name>
python3 run.py          # runs the corpus through gemma + DeepSeek, scores accuracy + reliability
```

Models default to a local Ollama model (`gemma4:12b`, zero egress) and DeepSeek (`deepseek-v4-flash`).
API keys are read from the environment, never committed.

## License

MIT — see [LICENSE](LICENSE).
