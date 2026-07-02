"""
Location: engine/guard.py
Purpose: Brake-pedal runtime guard (DESIGN T5) -- caps a benchmark run's model-call steps and
         estimated spend, tripping BEFORE a breach (fail closed), never after. Designed to wrap
         the actual call-site inside harness.run_harness(), not just live as an unused config
         value -- see the DESIGN doc's sad-path row: "guard is rendered in config but not wired
         to the runner... the exact dead-control trap."
Functions: BrakePedalGuard.before_call(), BrakePedalGuard.tripped_reason(), GuardTripped
Calls: none (pure; the caller decides how to log/report a trip)
Imports: dataclasses
"""

from dataclasses import dataclass, field
from typing import Optional


# Coarse per-call cost estimate (USD), keyed by the runner's model label (see engine/runner.py
# FAST_SET/BIG_BATCH). Local Ollama models are $0 (own hardware). Hosted estimates are a rough
# upper bound for one call at this harness's fixed shape (prompt = one document excerpt,
# max_tokens=1024 response) -- deliberately generous so the cap trips EARLY, never late.
ESTIMATED_COST_PER_CALL_USD = {
    "gemma3-1b": 0.0,
    "qwen3.5-27b": 0.0,
    "deepseek-v4f": 0.002,
    "gemini": 0.01,
    # Hosted OpenRouter models added for the 2026-07-02 parallel-execution sweep (Eikiyo: "start
    # with gemma from your list... we are not limited by laptop anymore"). Real per-call cost at
    # this harness's fixed shape (~470-item x 20-run sweep) is ~$0.0000543 (PTC $0.51 / 9400
    # calls, see artifacts/pricing_probity.html) -- ~2x that, not the ~50x margin used for
    # deepseek-v4f above, so a per-leaf guard cap doesn't trip long before a real run completes.
    "gemma3-1b-qat": 0.0,
    "gemma4-31b-or": 0.0001,
    # Remaining "10 recommended models" lineup, added 2026-07-03 for the auto-ramp sweep
    # (fastest-to-slowest by measured latency, excludes Anthropic agent-mode + DeepSeek per
    # Eikiyo). Same ~2x-real-PTC conservatism as gemma4-31b-or above.
    "mistral-large-or": 0.0005,
    "minimax-m2.5-or": 0.00012,
    "llama3.3-70b-or": 0.0001,
    "gemini3-flash-or": 0.0006,
    "gpt-oss-120b-or": 0.00003,
    "gpt5-mini-or": 0.0003,
    # Direct Anthropic API (api.anthropic.com), explicitly authorized 2026-07-03 -- real
    # Haiku 4.5 pricing $1/$5 per MTok, ~600 input / ~15 output tokens/call observed.
    "haiku-4.5-direct": 0.001,
}
# A model label the guard has no cost estimate for is treated as the most expensive known
# label, not $0 -- an unrecognized model must never get a free pass on the spend cap.
_UNKNOWN_MODEL_COST_USD = max(ESTIMATED_COST_PER_CALL_USD.values())


class GuardTripped(RuntimeError):
    """Raised by before_call() when making the next call would breach a configured cap.
    Callers must stop issuing calls on this exception -- catching it and calling before_call()
    again is a guard bypass."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


@dataclass
class BrakePedalGuard:
    """
    What: a per-run guard object, created fresh for each benchmark run and threaded through
          every model call in that run. before_call() must be invoked immediately before each
          LLMClient.generate() call and must raise GuardTripped (not return a bool) the moment
          the NEXT call would exceed a configured cap -- the cap is checked pre-call, so the
          guard can never be exceeded even by one call.
    max_steps: hard cap on total generate() calls this guard permits across its lifetime. None
               disables the step cap.
    max_cost_usd: hard cap on cumulative ESTIMATED spend (see ESTIMATED_COST_PER_CALL_USD).
                  None disables the cost cap.
    allowed_models: if given, before_call() trips immediately for any model_label not in this
                     set -- lets a run be scoped to only the models it was configured to use.
    """

    max_steps: Optional[int] = None
    max_cost_usd: Optional[float] = None
    allowed_models: Optional[frozenset] = None
    steps_taken: int = field(default=0, init=False)
    spend_usd: float = field(default=0.0, init=False)
    _tripped_reason: Optional[str] = field(default=None, init=False)

    def before_call(self, model_label: str) -> None:
        """Call immediately before issuing one generate() call. Raises GuardTripped and
        records the trip reason if this call would breach any configured cap; otherwise
        records the call as taken (steps_taken += 1, spend_usd += this call's estimate) and
        returns normally. A guard that has already tripped stays tripped -- it re-raises the
        SAME first reason on every subsequent call, it never resets mid-run."""
        if self._tripped_reason is not None:
            raise GuardTripped(self._tripped_reason)

        if self.allowed_models is not None and model_label not in self.allowed_models:
            self._trip(f"model '{model_label}' is not in the allowed set {sorted(self.allowed_models)}")

        if self.max_steps is not None and self.steps_taken + 1 > self.max_steps:
            self._trip(f"would exceed max_steps={self.max_steps} (already took {self.steps_taken})")

        call_cost = ESTIMATED_COST_PER_CALL_USD.get(model_label, _UNKNOWN_MODEL_COST_USD)
        if self.max_cost_usd is not None and self.spend_usd + call_cost > self.max_cost_usd:
            self._trip(
                f"would exceed max_cost_usd=${self.max_cost_usd:.4f} "
                f"(already spent ~${self.spend_usd:.4f}, next call ~${call_cost:.4f})"
            )

        self.steps_taken += 1
        self.spend_usd += call_cost

    def _trip(self, reason: str) -> None:
        self._tripped_reason = reason
        raise GuardTripped(reason)

    @property
    def tripped(self) -> bool:
        return self._tripped_reason is not None

    def tripped_reason(self) -> Optional[str]:
        return self._tripped_reason
