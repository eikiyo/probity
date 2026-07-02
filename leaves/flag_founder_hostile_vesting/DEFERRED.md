# DEFERRED — flag_founder_hostile_vesting leaf (8.4, stakes 4)

**Audit (2026-07-02, follow-up session):** Re-attempted sourcing per Eikiyo's "finish all 22
pending" directive. Searched the existing vesting_acceleration corpus (114 real cached docs)
for genuine "clawback"/"forfeiture of vested shares" language as a hostile indicator: found
hits, but on inspection they were routine SOX/Dodd-Frank-mandated public-company recoupment
policies (e.g. Globe Life Inc.'s standard "Clawback Policy" for financial restatements) --
not founder-hostile VC-financing terms. Ran fresh EDGAR full-text searches for "forfeit all
vested options" (30 hits) and "no acceleration of vesting" + "termination without cause" (912
hits); fetched 2 real candidates (McLeodUSA, Aperion Biologics) but neither contained the
matched phrase in the fetched exhibit (the FTS hit was evidently in a different sub-document
within the same accession, not the one fetched).

**Root cause:** Real "founder-hostile" vesting terms (board-discretion clawback of VESTED
equity, no acceleration whatsoever on any termination type, re-imposed cliffs on refresh
grants) are adversarial-to-the-employee by design and essentially never appear in SEC-filed
executive employment agreements or option plans -- those filings, by their nature, disclose
NEGOTIATED, investor/counsel-reviewed terms for named executive officers, which are
systematically the FRIENDLY end of the spectrum (this is the same selection-bias pattern
that made `option_pool_shuffle` and the exit_waterfall family hard: what actually gets
filed with the SEC is not representative of the full space of possible real-world terms).

**What would unblock this:** A genuinely adversarial source class not well-represented in
public company filings -- e.g. a private company's internal equity plan document obtained
via litigation exhibit (a wrongful-termination or breach-of-contract lawsuit where a
plaintiff's founder agreement is entered as an exhibit), or a direct pairing against
`vesting_acceleration`'s existing 3 real "no acceleration" items IF a genuine second real
document can be found stating an EXPLICIT contrasting "friendly" alternative for the same
company/round (not yet located).

source.py/task.py/run.py not yet created; genuinely unsourced, not fabricated to hit a count.
