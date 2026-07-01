# DEFERRED — s1_use_of_proceeds leaf (7.3)

## Status
A prior sibling-agent build shipped 59 items; independent audit rejected ALL 59 and this
leaf is reset to 0 items.

## What was wrong
The agent's EDGAR full-text search for "Use of Proceeds" surfaced the WRONG document types
and/or the wrong section of the right document. Spot-checking the first 3 of 59 items found:
- Blue Water Restaurant Group: the saved "validating_quote" is raw HTML/CSS style-attribute
  garbage (`font-family:Calibri...MARGIN-BOTTOM:-2px`), not any human-readable text at all.
- Alliance Petroleum Corp: the saved quote is from an SEC COMMENT LETTER / CORRESP filing
  discussing a company's Use of Proceeds SECTION ("revised disclosure in your Use of
  Proceeds section... your reference on your cover page to your offering of $500,000 appears
  to be a ty[po]") -- this is SEC staff correspondence ABOUT the section, not the actual S-1
  prospectus text stating the use of proceeds.
- SGX Pharmaceuticals: same pattern -- a comment-letter/correspondence excerpt referencing
  "Use of Proceeds" as a section name, not the real prospectus content.

This confirms the FTS phrase search matched the SECTION NAME appearing in unrelated document
types (SEC comment letters, amendment cover letters) rather than genuine S-1 prospectus body
text -- the same "keyword-is-candidate-not-oracle" failure class as `fully_diluted_basis`
earlier this session, at much larger scale (59 items, not caught by the agent's own str.find()
check because the check only confirms the excerpt is a literal substring of SOME fetched
document -- it does not confirm that document is the right TYPE).

## What's needed
A real S-1 (form type "S-1", not "CORRESP"/"UPLOAD"/"S-1/A" comment responses) with the
literal section heading "USE OF PROCEEDS" followed by real body text stating a specific use
(not just a dollar estimate with blank placeholders, per the Pinterest/Chewy draft-S-1 issue
found earlier this session in `current_ownership_pct`'s excluded list). Uber's real S-1
(CIK 1543151, accession 0001193125-19-103850) has a clean, complete example: "The principal
purposes of this offering are to increase our capitalization and financial flexibility and
to create a public market for our common stock. We intend to use the net proceeds we receive
from this offering for general corporate purposes, including working capital, operating
expenses, and capital expenditures." -- confirmed genuinely present in the real document.
Airbnb's cached S-1 text did not contain a "USE OF PROCEEDS" section at all (may be in an
untruncated portion not cached); Pinterest's and Chewy's found only the table-of-contents
page-number reference, not the actual section body, in the cached text.

Needs 5-9 more real S-1s (form type S-1 specifically, verified via
`https://data.sec.gov/submissions/CIK{cik}.json`) with genuinely stated, non-placeholder,
non-boilerplate uses of proceeds, each cross-checked to ensure the fetched document is really
form type S-1 and the excerpt is really the prospectus body, not a cover letter or amendment
correspondence about that section.

source.py deleted (its EDGAR search scoping was the root cause); rebuild from scratch when
resourced properly.
