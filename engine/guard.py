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
from typing import Dict, Optional


# --- Per-call cost, DERIVED from list prices rather than eyeballed -----------------------------
#
# WHY THIS WAS REBUILT (2026-07-27). The previous table held hand-picked "deliberately generous"
# constants, and generosity in a cost ESTIMATE is not conservative -- it is what makes a spend cap
# fire early. Combined with a flat $0.20 per-leaf cap it silently truncated 5 cells of the 0.7
# sweep, and because a missing item can never be counted as flipping, the missing data biased
# wobble DOWNWARD (models read as more reliable than they are):
#     participation_type/gemini3-flash-or  333 of 360   ($0.20 / $0.0006 = 333)
#     pre_vs_post_money/gemini3-flash-or   333 of 380
#     safe_pre_post/haiku-4.5-direct       199 of 320   ($0.20 / $0.0010 = 200)
#     safe_pro_rata_side_letter/haiku      199 of 300
#     safe_cap_vs_discount_applies/haiku   199 of 260
# deepseek-v4f was the worst offender at $0.002 against a real ~$0.00009, a 22x overstatement.
#
# Estimates are now COMPUTED from three measured inputs, so they are auditable and regenerable:
#   MEAN_PROMPT_TOKENS  measured over all 470 real prompts via each leaf's build_prompt()
#   ANSWER_TOKENS       every leaf scores exactly ONE field; the reply is a tiny JSON object
#   starve rate         share of 0.7-run calls that returned an EMPTY completion, i.e. burned the
#                       whole max_tokens budget on hidden reasoning. Counted from the committed
#                       checkpoints, not assumed: minimax 536/9400, gpt-oss 27/9400, gpt5-mini
#                       18/9400, gemini 1/9326, everything else 0.
# The remaining safety margin lives in the CAP (see caps_for_leaf), where it belongs -- a cap
# sized from the work actually owed, not a flat number that scales with nothing.
MEAN_PROMPT_TOKENS = 584
ANSWER_TOKENS = 25
REASONING_CAP_TOKENS = 16384          # OpenRouterClient max_tokens; a starved call bills all of it

# label: (input $/Mtok, output $/Mtok, starved-call fraction). Prices pulled live from the
# provider on 2026-07-27 (openrouter.ai/api/v1/models; ai.google.dev/gemini-api/docs/pricing).
MODEL_PRICING = {
    "deepseek-v4f":     (0.14, 0.28, 0.0),
    # deepseek-v4-pro, from api-docs.deepseek.com's own USD pricing page (fetched 2026-07-27):
    # $0.435/M input cache-miss, $0.87/M output. The cache-hit rate ($0.003625/M) is NOT assumed --
    # pricing a run as if it will hit cache understates the bill on the first pass through a corpus.
    "deepseek-v4p":     (0.435, 0.87, 0.0),
    "gemma4-31b-or":    (0.14, 0.40, 0.0),
    "mistral-large-or": (0.50, 1.50, 0.0),
    "minimax-m2.5-or":  (0.15, 0.90, 536 / 9400),
    "llama3.3-70b-or":  (0.13, 0.40, 0.0),
    "gemini3-flash-or": (0.50, 3.00, 1 / 9326),
    "gpt-oss-120b-or":  (0.037, 0.17, 27 / 9400),
    "gpt5-mini-or":     (0.25, 2.00, 18 / 9400),
    # Anthropic direct. The client marks the user block cache_control:ephemeral and the harness
    # sends the SAME prompt 20x per item, so input bills ~1 write (1.25x) + 19 reads (0.10x).
    "haiku-4.5-direct": (1.00 * (1 / 20 * 1.25 + 19 / 20 * 0.10), 5.00, 0.0),
}

# Local Ollama models: own hardware, genuinely $0. Kept explicit so a local label can never fall
# through to the unknown-model default and trip a cost cap that does not apply to it.
LOCAL_MODELS = ("gemma3-1b", "gemma3-1b-qat", "qwen3.5-27b", "gemma4-12b", "gemma4-12b-qat")


def per_call_cost(label: str) -> Optional[float]:
    """Expected USD for one call at this harness's fixed shape. None if the label is unknown --
    the caller decides the fail-closed default, this function never guesses."""
    if label in LOCAL_MODELS:
        return 0.0
    priced = MODEL_PRICING.get(label)
    if priced is None:
        return None
    in_usd, out_usd, starve = priced
    return (MEAN_PROMPT_TOKENS * in_usd
            + ANSWER_TOKENS * out_usd
            + starve * REASONING_CAP_TOKENS * out_usd) / 1e6


ESTIMATED_COST_PER_CALL_USD = {lab: 0.0 for lab in LOCAL_MODELS}
ESTIMATED_COST_PER_CALL_USD.update({lab: per_call_cost(lab) for lab in MODEL_PRICING})

# A model label the guard has no cost estimate for is treated as the most expensive known label,
# not $0 -- an unrecognized model must never get a free pass on the spend cap.
_UNKNOWN_MODEL_COST_USD = max(ESTIMATED_COST_PER_CALL_USD.values())

# The superseded hand-picked constants, kept ONLY so the regression test can demonstrate that the
# old table + a flat $0.20 cap really does reproduce the 5 historical truncations at their exact
# call counts (333, 333, 199, 199, 199). Without this, "the new caps do not truncate" would be an
# unfalsifiable green. Nothing in the live call path reads this.
ESTIMATED_COST_PER_CALL_USD_LEGACY = {
    "gemma3-1b": 0.0, "qwen3.5-27b": 0.0, "gemma3-1b-qat": 0.0,
    "deepseek-v4f": 0.002, "gemini": 0.01, "gemma4-31b-or": 0.0001,
    "mistral-large-or": 0.0005, "minimax-m2.5-or": 0.00012, "llama3.3-70b-or": 0.0001,
    "gemini3-flash-or": 0.0006, "gpt-oss-120b-or": 0.00003, "gpt5-mini-or": 0.0003,
    "haiku-4.5-direct": 0.001,
}

# How much headroom a per-leaf cap gets over the work that leaf actually owes. 3x absorbs a
# genuinely more expensive leaf (the longest prompt is ~4.8x the mean) and provider price drift,
# while still stopping a runaway loop long before it can spend real money.
CAP_MARGIN = 3.0


def caps_for_leaf(label: str, expected_calls: int,
                   margin: float = CAP_MARGIN) -> Dict[str, float]:
    """
    What: per-leaf guard caps sized from the work that leaf OWES (items x n_runs), instead of a
          flat constant. Returns {"max_steps", "max_cost_usd"} ready to splat into BrakePedalGuard.
    Why: a flat cap cannot distinguish a 1-item leaf from a 19-item one, so on a big leaf it fires
          mid-run (the 5 truncations above) while on a small leaf it is far too loose to catch
          anything. A cap derived from expected_calls is tight on every leaf at once.
    Fail-closed: an unknown label is priced at the most expensive known model, so a new model can
          only ever get a SMALLER cap than it deserves, never a free pass.
    """
    cost = per_call_cost(label)
    if cost is None:
        cost = _UNKNOWN_MODEL_COST_USD
    return {"max_steps": int(expected_calls * 1.1) + 1,
            "max_cost_usd": max(expected_calls * cost * margin, 0.01)}


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
