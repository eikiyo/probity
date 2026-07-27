"""
Location: engine/routing.py
Purpose: Record WHICH provider path served a cell, and what temperature was requested vs actually
         honoured, so the paper's appendix table is regenerable from disk instead of reconstructed
         from memory of how a sweep was launched. Routing is a first-class confound in a
         cross-model comparison (a gateway picks its own backend and quantization), so it is
         recorded per cell, never assumed from the model name.
Functions: routing_for(), honoured_temperature(), appendix_row()
Calls: none (pure; reads only the client's own class/attrs)
Imports: typing
"""

from typing import Any, Dict, Optional

# client class name -> the routing layer it represents. Keyed by NAME rather than by importing
# the classes, so this module stays import-light and cannot create a cycle with models.py.
_ROUTING_BY_CLIENT = {
    "OllamaClient": "ollama",
    "DeepSeekClient": "direct",
    "GeminiClient": "direct",
    "AnthropicClient": "direct",
    "OpenRouterClient": "openrouter",
    "MockClient": "mock",
}

# Providers that echo the sampling temperature back in their response body. As of 2026-07-27:
# NONE of them do. OpenAI-compatible /chat/completions (DeepSeek, OpenRouter) returns
# id/model/choices/usage and no sampling parameters; the Anthropic Messages API returns
# id/model/content/usage/stop_reason; Ollama /api/generate returns model/response/*_duration
# counters; Gemini generateContent returns candidates/usageMetadata. So `temperature_honoured` is
# genuinely UNKNOWN, not zero and not "confirmed equal to requested". It is reported as null with
# that stated, per the DESIGN doc's sad-path row 4 -- writing "0.1" there would be a fabrication.
_ECHOES_TEMPERATURE: Dict[str, bool] = {name: False for name in _ROUTING_BY_CLIENT}


def routing_for(client: Any) -> str:
    """The routing layer this client represents. An unrecognised client is reported as
    'unknown' rather than guessed into a bucket -- a wrong routing label would silently
    misattribute a confound."""
    return _ROUTING_BY_CLIENT.get(type(client).__name__, "unknown")


def honoured_temperature(client: Any, response: Optional[Dict[str, Any]] = None) -> Optional[float]:
    """
    What: the temperature the provider reports it actually used, or None when it reports nothing.
    Why it is almost always None: see _ECHOES_TEMPERATURE. The lookup is still implemented
          honestly (it reads the response if one is supplied and the provider is known to echo)
          so that if a provider starts returning the field, this captures it instead of
          continuing to report null out of habit.
    """
    if response is None or not _ECHOES_TEMPERATURE.get(type(client).__name__, False):
        return None
    for key in ("temperature", "sampling_temperature"):
        if isinstance(response.get(key), (int, float)):
            return float(response[key])
    gen_cfg = response.get("generationConfig")
    if isinstance(gen_cfg, dict) and isinstance(gen_cfg.get("temperature"), (int, float)):
        return float(gen_cfg["temperature"])
    return None


def appendix_row(label: str, model_id: Optional[str], routing: str,
                  requested: float, honoured: Optional[float]) -> Dict[str, Any]:
    """One row of the paper's requested-vs-honoured appendix table."""
    return {
        "label": label,
        "model_id": model_id,
        "routing": routing,
        "temperature_requested": requested,
        "temperature_honoured": honoured,
        "honoured_reported": honoured is not None,
    }


def render_appendix(rows) -> str:
    """Markdown appendix table. A provider that reports nothing renders as `null (not reported)`,
    never as the requested value -- the whole point is to not claim confirmation we do not have."""
    out = ["| Model | Routing | Temp requested | Temp honoured (provider-reported) |",
           "|---|---|---|---|"]
    for r in sorted(rows, key=lambda x: (x["routing"], x["label"])):
        hon = f"{r['temperature_honoured']}" if r["honoured_reported"] else "`null` (not reported)"
        name = r.get("model_id") or r["label"]
        out.append(f"| `{name}` | {r['routing']} | {r['temperature_requested']} | {hon} |")
    reported = sum(1 for r in rows if r["honoured_reported"])
    out += ["", f"*{reported} of {len(rows)} providers report the sampling temperature back in "
                "the response body. Where a provider reports nothing, the value is recorded as "
                "`null`: the request carried the temperature, but the provider offers no "
                "confirmation that it was applied, and asserting otherwise would be unfounded.*"]
    return "\n".join(out)
