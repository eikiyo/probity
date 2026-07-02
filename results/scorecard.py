"""
Location: results/scorecard.py
Purpose: Scorecard report (DESIGN T7) -- renders one leaf's scored run as a terminal report and
         an HTML report, honoring two invariants from the DESIGN doc: (1) a 0-task result NEVER
         renders a green headline (fail closed, show "0 tasks loaded", caller must exit non-zero
         on report.ok=False); (2) the denominator is always scored+errored, never silently fewer
         (n_instances - n_measurable is surfaced explicitly as "errored", not dropped).
Functions: build_report(), render_terminal(), render_html(), ModelRow, ScorecardReport
Calls: none (pure formatting over an already-scored dict; see engine/scorer.py for scoring)
Imports: dataclasses, html
"""

from dataclasses import dataclass, field
from html import escape
from typing import Any, Dict, List, Optional


@dataclass
class ModelRow:
    model: str
    n_instances: int
    n_measurable: int
    accuracy_majority: float
    consistency_pct: float

    @property
    def n_errored(self) -> int:
        return self.n_instances - self.n_measurable


@dataclass
class ScorecardReport:
    leaf_name: str
    rows: List[ModelRow] = field(default_factory=list)
    guard_stats: Optional[Dict[str, Any]] = None
    ok: bool = True
    empty_reason: Optional[str] = None


def build_report(leaf_name: str, scored: Dict[str, Dict[str, Any]],
                  guard_stats: Optional[Dict[str, Any]] = None) -> ScorecardReport:
    """
    What: turns a leaf's scored.json-shaped dict ({model_label: {"model", "accuracy",
          "reliability"}}, as written by engine/runner.py) into a ScorecardReport.
    Fail-closed rule: if `scored` is empty, OR every model row has n_instances == 0, the report
          is marked NOT ok with an explicit empty_reason -- render_terminal/render_html both
          honor this and refuse to print a headline score, per the DESIGN screens spec.
    """
    if not scored:
        return ScorecardReport(leaf_name=leaf_name, rows=[], guard_stats=guard_stats,
                                ok=False, empty_reason="0 tasks loaded — check data version")

    rows = []
    for label, res in scored.items():
        acc = res.get("accuracy", {})
        rel = res.get("reliability", {})
        rows.append(ModelRow(
            model=res.get("model", label),
            n_instances=acc.get("n_instances", 0),
            n_measurable=acc.get("n_measurable", 0),
            accuracy_majority=acc.get("accuracy_majority", 0.0),
            consistency_pct=rel.get("consistency_pct", 0.0),
        ))

    if all(r.n_instances == 0 for r in rows):
        return ScorecardReport(leaf_name=leaf_name, rows=rows, guard_stats=guard_stats,
                                ok=False, empty_reason="0 tasks loaded — check data version")

    return ScorecardReport(leaf_name=leaf_name, rows=rows, guard_stats=guard_stats, ok=True)


def _guard_line(guard_stats: Optional[Dict[str, Any]]) -> str:
    if guard_stats is None:
        return "guard: n/a"
    if guard_stats.get("guard_tripped"):
        return f"guard: TRIPPED — {guard_stats.get('guard_reason', 'unknown reason')}"
    return "guard: ok (not tripped)"


def render_terminal(report: ScorecardReport) -> str:
    lines = [f"=== Scorecard: {report.leaf_name} ==="]
    if not report.ok:
        lines.append(f"REFUSED TO RENDER: {report.empty_reason}")
        lines.append(_guard_line(report.guard_stats))
        return "\n".join(lines)

    for row in report.rows:
        lines.append(
            f"{row.model}: {row.n_measurable}/{row.n_instances} scored "
            f"({row.n_errored} errored) — correctness {row.accuracy_majority:.2f}, "
            f"consistency {row.consistency_pct:.0f}%"
        )
    lines.append(_guard_line(report.guard_stats))
    return "\n".join(lines)


def render_html(report: ScorecardReport) -> str:
    if not report.ok:
        return (
            "<html><head><title>Probity scorecard</title></head><body>"
            f"<h1>{escape(report.leaf_name)}</h1>"
            f"<p class='refused'>{escape(report.empty_reason or '0 tasks loaded')}</p>"
            f"<p>{escape(_guard_line(report.guard_stats))}</p>"
            "</body></html>"
        )

    rows_html = "".join(
        f"<tr><td>{escape(r.model)}</td><td>{r.n_measurable}/{r.n_instances}</td>"
        f"<td>{r.n_errored}</td><td>{r.accuracy_majority:.2f}</td>"
        f"<td>{r.consistency_pct:.0f}%</td></tr>"
        for r in report.rows
    )
    return (
        "<html><head><title>Probity scorecard</title></head><body>"
        f"<h1>{escape(report.leaf_name)}</h1>"
        "<table><tr><th>model</th><th>scored/total</th><th>errored</th>"
        "<th>correctness</th><th>consistency</th></tr>"
        f"{rows_html}</table>"
        f"<p>{escape(_guard_line(report.guard_stats))}</p>"
        "</body></html>"
    )
