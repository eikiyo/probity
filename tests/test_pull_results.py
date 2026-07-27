"""
Location: tests/test_pull_results.py
Purpose: Pin kaggle-arm/pull_results.py. The single load-bearing behaviour is a REFUSAL: an
         archive containing a legacy-namespace results file must never be extracted, because
         doing so would overwrite the published 0.7 baseline that is the other half of the paired
         comparison. Every test builds a real tarball rather than mocking tarfile, so the
         name-matching is exercised against real archive members.
Functions: TestLegacyDetection, TestRefusesToExtract, TestExtractsACleanArchive, TestFailsClosed
Imports: sys, tarfile, pytest, pathlib, pull_results
"""

import json
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "kaggle-arm"))

import pull_results  # noqa: E402


def make_tgz(path, names):
    """A real gzipped tar with one tiny file per name."""
    src = path.parent / "_src"
    src.mkdir(exist_ok=True)
    with tarfile.open(path, "w:gz") as tf:
        for n in names:
            f = src / Path(n).name
            # `scored*.json` goes through the MERGE path, which parses it. A fixture writing
            # junk there tested the extractor against input the real pipeline never produces.
            f.write_text("{}" if n.endswith(".json") else "x")
            tf.add(f, arcname=n)
    return path


class TestLegacyDetection:
    def test_unsuffixed_runs_file_is_legacy(self):
        assert pull_results.legacy_members(["leaves/a/runs_gemma3-1b.jsonl"])

    def test_unsuffixed_scored_file_is_legacy(self):
        assert pull_results.legacy_members(["leaves/a/scored.json"])

    @pytest.mark.parametrize("name", [
        "leaves/a/runs_t01_gemma3-1b.jsonl",
        "leaves/a/runs_t07_gemma3-1b.jsonl",
        "leaves/a/scored_t01.json",
        "leaves/a/scored_t07.json",
        "leaves/a/manifest_gemma3-1b.json",
    ])
    def test_arm_namespaced_files_are_not_legacy(self, name):
        """The negative control. A guard that flagged every member would pass every refusal test
        while making the pull permanently impossible."""
        assert pull_results.legacy_members([name]) == []

    def test_a_label_beginning_with_t_is_not_mistaken_for_an_arm_infix(self):
        """`runs_tuned-v4.jsonl` is a fine-tune label in the LEGACY namespace, not arm t-something.
        The infix pattern requires digits, so a label starting with 't' cannot smuggle a legacy
        file past the guard."""
        assert pull_results.legacy_members(["leaves/a/runs_tuned-v4.jsonl"])


class TestRefusesToExtract:
    def test_an_archive_with_a_legacy_file_is_rejected_whole(self, tmp_path):
        """Rejected WHOLE, not partially extracted: an archive containing a legacy-arm file comes
        from a producer we no longer trust to have namespaced anything else correctly."""
        tgz = make_tgz(tmp_path / "bad.tgz",
                       ["leaves/a/runs_t01_gemma3-1b.jsonl", "leaves/a/scored.json"])
        dest = tmp_path / "out"
        dest.mkdir()
        with pytest.raises(SystemExit) as e:
            pull_results.extract(tgz, dest)
        assert "refusing to extract" in str(e.value)
        assert list(dest.iterdir()) == [], "nothing may be written when the archive is refused"

    def test_a_path_escape_is_rejected(self, tmp_path):
        tgz = make_tgz(tmp_path / "esc.tgz", ["../outside.json"])
        with pytest.raises(SystemExit):
            pull_results.extract(tgz, tmp_path / "out")

    def test_the_refusal_names_the_offending_member(self, tmp_path):
        tgz = make_tgz(tmp_path / "bad.tgz", ["leaves/a/scored.json"])
        ok, problems = pull_results.verify_archive(tgz)
        assert ok is False
        assert any("scored.json" in p for p in problems)


class TestExtractsACleanArchive:
    def test_a_clean_archive_extracts_every_member(self, tmp_path):
        names = ["leaves/a/runs_t01_gemma3-1b.jsonl", "leaves/a/scored_t01.json",
                 "leaves/b/runs_t07_gemma3-1b-qat.jsonl", "leaves/b/scored_t07.json"]
        tgz = make_tgz(tmp_path / "good.tgz", names)
        dest = tmp_path / "out"
        dest.mkdir()
        pull_results.extract(tgz, dest)
        for n in names:
            assert (dest / n).exists(), n

    def test_dry_run_writes_nothing(self, tmp_path):
        tgz = make_tgz(tmp_path / "good.tgz", ["leaves/a/scored_t01.json"])
        dest = tmp_path / "out"
        dest.mkdir()
        pull_results.extract(tgz, dest, dry_run=True)
        assert list(dest.iterdir()) == []


class TestFailsClosed:
    def test_an_unreadable_archive_is_refused_not_treated_as_empty(self, tmp_path):
        bad = tmp_path / "corrupt.tgz"
        bad.write_bytes(b"not a tarball")
        ok, problems = pull_results.verify_archive(bad)
        assert ok is False
        assert any("cannot read" in p for p in problems)

    def test_an_empty_archive_is_refused(self, tmp_path):
        """A kernel that produced nothing is a failed kernel. Extracting its empty archive would
        report success and leave the arm silently unmeasured."""
        tgz = tmp_path / "empty.tgz"
        with tarfile.open(tgz, "w:gz"):
            pass
        ok, problems = pull_results.verify_archive(tgz)
        assert ok is False
        assert any("empty" in p for p in problems)


class TestAgainstTheRealPushedHarness:
    def test_the_harness_we_actually_pushed_carries_no_results(self):
        """Ties the guard to the real artifact: pack.sh's exclude list is a comment until
        something checks it. If a future re-pack drops an exclude, this goes red here rather than
        after the kernel hands the baseline back."""
        harness = ROOT / "kaggle-arm" / "probity-arm-harness.tgz"
        if not harness.exists():
            pytest.skip("harness tarball not built in this checkout")
        with tarfile.open(harness, "r:gz") as tf:
            names = tf.getnames()
        assert pull_results.legacy_members(names) == []
        # `._`-prefixed entries are macOS AppleDouble sidecars (163-byte resource forks). BSD
        # `tar tzf` FILTERS them from its listing while Python's tarfile shows them, so the same
        # archive reads as 60 oracle files through the CLI and 120 through Python. Neither tool is
        # wrong; a count that does not say which view it took is. Filtered here so the assertion
        # means "60 real oracle files", which is the fact worth pinning.
        real = [n for n in names if not Path(n).name.startswith("._")]
        assert sum(1 for n in real if n.endswith("oracle.jsonl")) == 60


class TestSharedScoredFilesAreMergedNotOverwritten:
    """The near-miss of 2026-07-27. `scored_t01.json` is ONE file per leaf holding EVERY model
    label. The Kaggle kernel starts from a clean slate, so its copy holds exactly one label --
    and a tar extract REPLACES. Extracting it over a local file holding the ten hosted models
    would have deleted the entire hosted t01 arm's scoring, across all 60 leaves, silently.

    The legacy guard does NOT catch this: scored_t01.json is arm-namespaced and passes it. A
    guard that protects one arm is not a guard that protects the data."""

    def test_a_shared_scored_file_is_classified_as_shared(self):
        assert pull_results.is_shared("leaves/a/scored_t01.json")
        assert pull_results.is_shared("leaves/a/scored_t07.json")
        assert pull_results.is_shared("leaves/a/scored.json")

    def test_per_label_files_are_not_shared(self):
        """Negative control: if everything were classified shared, nothing would extract."""
        assert not pull_results.is_shared("leaves/a/runs_t01_gemma3-1b.jsonl")
        assert not pull_results.is_shared("leaves/a/manifest_t01_gemma3-1b.json")

    def test_merging_preserves_every_pre_existing_label(self, tmp_path):
        existing = tmp_path / "scored_t01.json"
        existing.write_text(json.dumps({f"hosted-{i}": {"v": i} for i in range(10)}))
        res = pull_results.merge_scored(existing, json.dumps({"gemma3-1b-qat": {"v": 99}}).encode())
        merged = json.loads(existing.read_text())
        assert len(merged) == 11
        assert res["added"] == ["gemma3-1b-qat"]
        assert all(f"hosted-{i}" in merged for i in range(10))
        assert merged["gemma3-1b-qat"]["v"] == 99

    def test_merging_into_a_missing_file_just_writes_it(self, tmp_path):
        target = tmp_path / "scored_t07.json"
        pull_results.merge_scored(target, json.dumps({"gemma3-1b": {"v": 1}}).encode())
        assert json.loads(target.read_text()) == {"gemma3-1b": {"v": 1}}

    def test_incoming_data_wins_for_the_same_label(self, tmp_path):
        """A re-pull of the same kernel must be idempotent and must refresh, not duplicate."""
        target = tmp_path / "scored_t01.json"
        target.write_text(json.dumps({"gemma3-1b-qat": {"v": "old"}}))
        pull_results.merge_scored(target, json.dumps({"gemma3-1b-qat": {"v": "new"}}).encode())
        assert json.loads(target.read_text())["gemma3-1b-qat"]["v"] == "new"

    def test_full_extract_merges_shared_and_writes_per_label(self, tmp_path):
        """End to end on a real tarball: the pre-existing hosted labels must survive."""
        leaf = tmp_path / "repo" / "leaves" / "a"
        leaf.mkdir(parents=True)
        (leaf / "scored_t01.json").write_text(json.dumps({"hosted-model": {"v": 1}}))

        src = tmp_path / "src" / "leaves" / "a"
        src.mkdir(parents=True)
        (src / "scored_t01.json").write_text(json.dumps({"gemma3-1b-qat": {"v": 2}}))
        (src / "runs_t01_gemma3-1b-qat.jsonl").write_text('{"run":1}\n')
        tgz = tmp_path / "arm.tgz"
        with tarfile.open(tgz, "w:gz") as tf:
            tf.add(src / "scored_t01.json", arcname="leaves/a/scored_t01.json")
            tf.add(src / "runs_t01_gemma3-1b-qat.jsonl",
                   arcname="leaves/a/runs_t01_gemma3-1b-qat.jsonl")

        pull_results.extract(tgz, tmp_path / "repo")
        merged = json.loads((leaf / "scored_t01.json").read_text())
        assert set(merged) == {"hosted-model", "gemma3-1b-qat"}, "a pre-existing label was lost"
        assert (leaf / "runs_t01_gemma3-1b-qat.jsonl").exists()
