# DEFERRED — round_size leaf (1.2.1)

Audit (2026-07-01): agent sourced 8 "round size" items; ALL 8 failed audit:
- Occidental Petroleum (x3, $700M/$650M/$650M): a corporate DEBT TENDER OFFER ("Pool 1/2/3 Notes
  Maximum Purchase Price") -- a massive oil & gas company's note repurchase, nothing to do with
  venture financing or preferred stock rounds at all. Wrong company type, wrong instrument.
- Vodavi Technology ($31.2M): M&A acquisition consideration, not a financing round raise.
- "Technology Company 2008" ($5.25M): placeholder company name; describes a NOTES financing
  aggregate, not a priced preferred-stock round.
- "Technology Company Series Funding" ($15M): placeholder company name; the $15M figure is NOT
  stated in the excerpt at all -- it references "Exhibit A" (not shown) for the actual amount.
  Ungrounded from the shown text.
- "Public Company IPO 2021" ($46M): placeholder company name; an S-1 cover-page fee-calculation
  placeholder ("proposed maximum aggregate offering price"), not the actual round size, and an
  IPO is not a Series A-E preferred-stock financing round (wrong topic entirely).
- Vertical Communications Series E ($22M): the excerpt states "22,000 shares ... at $1,000 per
  share" -- the model would have to COMPUTE 22,000 x $1,000, not read a stated $22M figure. Also
  hedged with "at least 22,000 shares" (a floor, not necessarily the final round size).

Own audit found this field genuinely hard to source cleanly: most "aggregate purchase price of $X"
EDGAR hits turn out to be common-stock private placements (wrong instrument), M&A consideration
(wrong transaction type), or one investor's slice of a larger multi-investor round (not the round
total). One clean survivor found and kept as a head-start for the next pass:
  - Jazz Semiconductor Inc (participation_type/1200720_000104746904001493): "RF Micro Devices
    purchased 13,071,888 shares of our series B preferred stock for an aggregate purchase price
    of $60.0 million" -- genuinely Series B preferred, single clearly-stated aggregate.

Needs 5-7 more genuinely clean Series A-E preferred-stock TOTAL round statements (not per-investor
slices, not common stock, not M&A) before this can ship. source.py/task.py/run.py kept as
scaffolding; oracle.jsonl removed.
