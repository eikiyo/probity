# DEFERRED — s1_risk_factors leaf (7.4, stakes 2)

## Status
No validated real items sourced this session. Sourcing wall encountered on heading extraction.

## What this leaf needs
Extract HEADING text (not full paragraph) of risk factors from S-1 "Risk Factors" section. A valid oracle item requires:
- A real S-1 filing's Risk Factors section
- An identified risk-factor heading (the bolded/styled title line)
- Exact heading text copy-pasted from the document
- The heading isolated in corpus/questions as the question the model sees

## Why it's hard to source
- Risk factor headings in S-1 filings are often embedded in HTML/XML with variable formatting (sometimes wrapped in `<strong>`, sometimes all-caps, sometimes mixed case)
- Current extraction logic (looking for all-caps lines or lines with "risk" keyword) was too simplistic
- HTML parsing from EDGAR full-text search results requires proper tag-stripping to identify formatting
- A proper heading vs. a subheading vs. a narrative line is ambiguous without structured XML parsing

## Recommendation
Defer until either:
- (a) Implement proper HTML/XML heading tag detection (`<B>`, `<STRONG>`, `<heading>` tags in S-1 documents) before extracting, or
- (b) Manually audit a real S-1's Risk Factors section to identify the exact heading patterns and their encoding, then hard-code a more precise regex/parser, or
- (c) Reframe the task to extract "the FIRST statement in a named risk factor" (a full sentence, not just the heading) which is more reliably grounded in plain text

`task.py` and `run.py` are scaffolded and ready; `source.py` needs a better extraction strategy.
