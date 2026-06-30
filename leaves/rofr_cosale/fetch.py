"""
Location: leaves/rofr_cosale/fetch.py
Purpose: Candidate pool for the rofr_cosale leaf (5.5) is REUSED from leaves/drag_along/corpus/full
         (zero fresh EDGAR fetch -- same stockholder/transfer-agreement pool already on disk, per the
         rights_governance corpus-reuse finding: one fetch round seeds 4-5 sibling leaves). This script
         documents the provenance; the actual copy was a one-time `cp` from drag_along's corpus.
Functions: REUSED_FROM (provenance record)
Imports: none
"""

REUSED_FROM = "leaves/drag_along/corpus/full"
REUSED_IDS = [
    "0000912057-13-000222_filename4", "0000950123-14-005490_filename11",
    "0000950144-02-006194_g76584exv4w7", "0001683168-22-000097_aclarion_ex1008",
    "0000912057-17-000020_filename4", "0000912057-01-534636_a2059793zex-10_20",
    "0000891020-07-000003_v25599a1exv9w1", "0001493152-16-016248_ex10-1",
    "0001628280-19-001592_tmhc-123118xex1031", "0001077048-05-000165_ex10-1",
    "0001144204-04-017555_v08033_green", "0001193125-21-224403_d93222dex105",
]

if __name__ == "__main__":
    print(f"reused {len(REUSED_IDS)} docs from {REUSED_FROM} -- no fresh fetch for this leaf")
