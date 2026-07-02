"""
Location: projects/AI-PM/Knowledge/probe/models.py
Purpose: LLM client abstraction (DeepSeek hosted + Gemini hosted + Ollama local + OpenRouter
         gateway) with one interface. DeepSeek and OpenRouter share one retry-on-transient-error
         helper (_post_chat_completion) -- both are OpenAI-compat /chat/completions endpoints.
Functions: DeepSeekClient.generate(), GeminiClient.generate(), OllamaClient.generate(),
           OpenRouterClient.generate(), _post_chat_completion()
Calls: (urllib.request, json)
Imports: urllib.request, json, os, time, abc
"""

import urllib.request
import urllib.error
import json
import os
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class LLMClient(ABC):
    """Base class for LLM clients."""

    @abstractmethod
    def generate(self, prompt: str, temperature: float) -> str:
        """Generate text. Fail closed + observable on error."""
        pass


def _post_with_retry(url, headers, payload, timeout, error_label,
                      retryable_codes, max_attempts, backoff_base_seconds, extract_content):
    """
    What: shared retry-on-transient-error POST for any JSON HTTP LLM endpoint. Used by
          DeepSeekClient, OpenRouterClient, and AnthropicClient -- extracted 2026-07-03 (rule of
          two: a second near-identical retry loop was about to be pasted for OpenRouterClient,
          then a THIRD near-identical one for AnthropicClient, whose response shape differs from
          the OpenAI-compat providers -- content[0].text, not choices[0].message.content -- hence
          the extract_content callback instead of a hardcoded response path).
    Why: see DeepSeekClient.generate()'s original docstring (94% of one leaf's "parse failures"
          were raw 503s with zero retry, mismeasured as model unreliability) -- the exact same
          transient-vs-genuine-failure distinction applies to every hosted provider here.
    Output: extract_content(parsed_json_response) -- a callable, since each provider shapes its
            response differently. Raises RuntimeError (never a raw urllib exception) on a
            non-retryable error or after max_attempts genuinely transient ones.
    """
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST",
    )
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return extract_content(result)
        except urllib.error.HTTPError as e:
            last_error = e
            if e.code not in retryable_codes or attempt == max_attempts:
                raise RuntimeError(f"{error_label} generation failed: HTTP Error {e.code}: {e.reason}")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last_error = e
            if attempt == max_attempts:
                raise RuntimeError(f"{error_label} generation failed: {e}")
        except Exception as e:
            raise RuntimeError(f"{error_label} generation failed: {e}")
        time.sleep(backoff_base_seconds * attempt)
    raise RuntimeError(f"{error_label} generation failed after {max_attempts} attempts: {last_error}")


def _post_chat_completion(url, headers, payload, timeout, error_label,
                           retryable_codes, max_attempts, backoff_base_seconds):
    """Thin wrapper over _post_with_retry() for OpenAI-compat /chat/completions providers
    (DeepSeek, OpenRouter) -- kept as its own name so existing call sites are untouched."""
    return _post_with_retry(
        url, headers, payload, timeout, error_label, retryable_codes, max_attempts,
        backoff_base_seconds, extract_content=lambda r: r["choices"][0]["message"]["content"],
    )


class DeepSeekClient(LLMClient):
    """OpenAI-compat DeepSeek client (v4-flash)."""

    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "DEEPSEEK_API_KEY not set. Source secrets/.env first."
            )
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-v4-flash"

    # Transient HTTP status codes worth retrying (server-side/overload conditions) -- NOT 4xx
    # codes like 400/401 that indicate a real, non-recoverable problem with the request itself.
    _RETRYABLE_HTTP_CODES = {429, 500, 502, 503, 504}
    _MAX_ATTEMPTS = 3
    _BACKOFF_BASE_SECONDS = 2  # attempt 1 waits 2s, attempt 2 waits 4s, before the 3rd/final try.

    def generate(self, prompt: str, temperature: float) -> str:
        """
        What: sends one chat-completion request to DeepSeek and returns the raw text content.
        Why RETRY exists here (added on adversarial audit, 2026-07-02 -- see vault/mistakes.md):
             this method used to make exactly ONE HTTP attempt and treat ANY exception --
             including a transient `HTTP 503 Service Unavailable` -- identically to a genuine
             model output failure. Empirically, on liquidation_waterfall_payout's N=20 benchmark
             run, 17 of 18 "failures" (94%) were raw 503s, not the model doing anything wrong --
             the harness was silently mis-measuring API availability as model unreliability.
             This retries ONLY on transient/server-side conditions (5xx, 429 rate-limit, and
             network-level errors) with a short exponential backoff; a genuine 4xx (bad request,
             auth failure) is NOT retried since retrying a malformed request just wastes time.
        Output: the model's raw text response (still needs JSON-parsing by the caller -- this
                function's job is "did we get a response from the API," not "was it valid JSON").
        Success criteria: after this fix, a transient 503 during a bulk N=20 run should mostly
                self-heal within the same run (2-6s of backoff) instead of permanently dropping
                that one data point -- expect parse_failure_rate driven by genuine model-output
                issues to trend toward the TRUE model-reliability signal, not API noise. Fails
                closed (raises, same as before) only after _MAX_ATTEMPTS genuinely transient
                failures, or immediately on any non-retryable error -- never silently swallowed.
        """
        if temperature <= 0:
            raise ValueError(f"Temperature must be >0 (got {temperature}). SP1: no determinism.")

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            # Output is a small JSON object — 1024 is generous headroom, not a constraint.
            "max_tokens": 1024,
            # v4-flash DEFAULTS to thinking mode, which ignores temperature AND can burn the
            # whole budget on reasoning_content (empty content, finish_reason=length). The probe
            # measures direct-answer reliability at temp>0, so disable thinking (docs: thinking_mode).
            "thinking": {"type": "disabled"},
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        # Reasoning models (v4-flash) think longer on compute tasks — 30s was too tight
        # (cap_table timed out); 120s gives headroom without hanging the bulk run.
        return _post_chat_completion(
            self.base_url, headers, payload, timeout=120, error_label="DeepSeek",
            retryable_codes=self._RETRYABLE_HTTP_CODES, max_attempts=self._MAX_ATTEMPTS,
            backoff_base_seconds=self._BACKOFF_BASE_SECONDS,
        )


class GeminiClient(LLMClient):
    """Google Gemini client (generateContent). Default gemini-3.1-pro-preview (frontier 3.1 peer)."""

    def __init__(self, model: str = "gemini-3.1-pro-preview"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not set. Source secrets/.env first.")
        self.model = model
        self.base_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        )

    def generate(self, prompt: str, temperature: float) -> str:
        """Generate via Gemini. Assert temp > 0 (SP1)."""
        if temperature <= 0:
            raise ValueError(f"Temperature must be >0 (got {temperature}). SP1: no determinism.")

        try:
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    # JSON answer is tiny; headroom so thinking tokens don't starve the content.
                    "maxOutputTokens": 4096,
                    # Gemini 3.x defaults to thinking. The probe measures direct-answer reliability,
                    # so request the minimum reasoning the model allows (parity with DeepSeek/gemma).
                    "thinkingConfig": {"thinkingLevel": "low"},
                },
            }
            req = urllib.request.Request(
                self.base_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"x-goog-api-key": self.api_key, "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            cands = result.get("candidates", [])
            if not cands:  # safety block / empty — observable parse failure downstream, never silent
                return ""
            parts = cands[0].get("content", {}).get("parts", [])
            return "".join(p.get("text", "") for p in parts)

        except Exception as e:
            raise RuntimeError(f"Gemini generation failed: {e}")


class AnthropicClient(LLMClient):
    """
    Direct Anthropic Messages API client (api.anthropic.com) -- explicitly authorized by Eikiyo
    2026-07-03 ("run directly, you have the claude direct API") for the "10 recommended models"
    Claude-agent-mode seats, AFTER checking OpenRouter's anthropic/claude-haiku-4.5 listing was
    priced identically ($1/$5 per MTok, no OR discount) -- direct is simpler with no cost
    disadvantage. Per Kage root CLAUDE.md Sec 0.10, a bare "Haiku/Sonnet agent" normally means
    the in-chat Agent tool, NEVER api.anthropic.com without explicit approval -- this class is
    that explicit, scoped exception, used ONLY by this benchmark's own harness, never by a
    `claude` CLI subprocess (the landmine that silently bills this same key).
    Response shape differs from the OpenAI-compat providers: content[0].text, not
    choices[0].message.content -- see _post_with_retry()'s extract_content callback.
    No `thinking` parameter is ever set -- extended thinking is opt-in on this API, so omitting
    it entirely means zero thinking-token cost by default, not something to "turn down to zero."
    Prompt caching (2026-07-03, Eikiyo: "don't we get benefit of caching?"): the harness calls
    generate() with the SAME prompt string N=20 times per item (temperature is what varies the
    output, not the input -- see run_harness()'s N_RUNS loop) -- exactly the repeated-identical-
    prefix shape prompt caching is for. The user content block below is marked
    cache_control: ephemeral, so within a cache's 5-minute window the first call for an item
    pays a 1.25x write, and repeats pay 0.1x read instead of full price -- roughly an 80%+ cut
    on input cost, which dominates this workload's spend (a few hundred input tokens per call
    vs. a short JSON/bare-value answer). Concurrent calls for the SAME item can still race the
    first cache write (this client doesn't serialize per-item), so the realized saving is lower
    than the theoretical ceiling under high per-item concurrency -- still a real, one-line win.
    """

    _RETRYABLE_HTTP_CODES = {429, 500, 502, 503, 504}
    _MAX_ATTEMPTS = 3
    _BACKOFF_BASE_SECONDS = 2

    def __init__(self, model: str = "claude-haiku-4-5-20251001"):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set. Source secrets/.env first.")
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = model

    def generate(self, prompt: str, temperature: float) -> str:
        """Generate via the Anthropic Messages API. Assert temp > 0 (SP1)."""
        if temperature <= 0:
            raise ValueError(f"Temperature must be >0 (got {temperature}). SP1: no determinism.")

        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "temperature": temperature,
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": prompt, "cache_control": {"type": "ephemeral"}},
            ]}],
        }
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        def _extract(result):
            blocks = result.get("content", [])
            return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")

        return _post_with_retry(
            self.base_url, headers, payload, timeout=120, error_label=f"Anthropic({self.model})",
            retryable_codes=self._RETRYABLE_HTTP_CODES, max_attempts=self._MAX_ATTEMPTS,
            backoff_base_seconds=self._BACKOFF_BASE_SECONDS, extract_content=_extract,
        )


class OllamaClient(LLMClient):
    """Local Ollama client -- model is caller-supplied, no default (every real call site already
    passes one explicitly; see engine/runner.py's FAST_SET/BIG_BATCH)."""

    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = model

    def generate(self, prompt: str, temperature: float) -> str:
        """Generate via Ollama. Assert temp > 0 (SP1)."""
        if temperature <= 0:
            raise ValueError(f"Temperature must be >0 (got {temperature}). SP1: no determinism.")

        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "think": False,  # gemma4 is thinking-capable; the probe wants the direct answer (docs: /api/generate)
                "options": {
                    # MUST be nested under "options" — Ollama silently IGNORES a top-level temperature.
                    "temperature": temperature,
                    "num_predict": 1024,
                },
            }

            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "")

        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {e}")


class OpenRouterClient(LLMClient):
    """
    Hosted multi-model gateway (OpenAI-compat /chat/completions) -- lets Probity run any model
    OpenRouter serves (e.g. "google/gemma-4-31b-it") without a dedicated per-lab client class.
    Reuses DeepSeekClient's retry contract via the shared _post_chat_completion() helper.
    """

    _RETRYABLE_HTTP_CODES = {429, 500, 502, 503, 504}
    _MAX_ATTEMPTS = 3
    _BACKOFF_BASE_SECONDS = 2

    def __init__(self, model: str):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set. Source secrets/.env first.")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = model

    def generate(self, prompt: str, temperature: float) -> str:
        """Generate via OpenRouter. Assert temp > 0 (SP1)."""
        if temperature <= 0:
            raise ValueError(f"Temperature must be >0 (got {temperature}). SP1: no determinism.")

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            # 16384, not 1024: a reasoning-tier model (e.g. minimax-m2.5, gpt-5-mini) spends
            # most of its budget on a hidden "reasoning" content block before ever emitting the
            # visible JSON answer -- at 1024 that reasoning alone exhausted the cap and the model
            # returned an EMPTY completion 60-70% of the time on the harder leaves (root-caused
            # 2026-07-03: confirmed via a raw API call showing populated `reasoning` +
            # `finish_reason: "stop"` on a call that worked). 8192 still wasn't enough for
            # gpt-5-mini on the ownership-math leaves (41-43% still empty) -- 16384 per Eikiyo
            # ("do the pass, with high limits"). The JSON answer itself is tiny; all of this
            # headroom is for reasoning tokens, not the answer. Cost is bounded by actual usage,
            # not this ceiling -- a model that finishes at 400 reasoning tokens still only bills
            # ~400, this only raises the cap before truncation.
            "max_tokens": 16384,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            # OpenRouter's own attribution headers (optional, harmless) -- lets a model provider
            # see traffic came from this project on OpenRouter's public leaderboards.
            "HTTP-Referer": "https://github.com/eikiyo/probity",
            "X-Title": "Probity",
        }
        return _post_chat_completion(
            self.base_url, headers, payload, timeout=120, error_label=f"OpenRouter({self.model})",
            retryable_codes=self._RETRYABLE_HTTP_CODES, max_attempts=self._MAX_ATTEMPTS,
            backoff_base_seconds=self._BACKOFF_BASE_SECONDS,
        )


class MockClient(LLMClient):
    """Mock client for testing (returns canned varied outputs)."""

    def __init__(self, seed: int = 42):
        import random

        random.seed(seed)
        self.seed = seed
        self.call_count = 0

    def generate(self, prompt: str, temperature: float) -> str:
        """Return mock output that varies by temperature and call count."""
        import random

        random.seed(self.seed + self.call_count)
        self.call_count += 1

        if "term_sheet" in prompt.lower() or "extraction" in prompt.lower():
            base = {"valuation": 10000000, "investment_amount": 1000000}
            if temperature > 0.7:
                base["valuation"] = 9500000  # Vary by temp
            return json.dumps(base)
        elif "cap_table" in prompt.lower():
            base = {
                "founder_ownership_pct": 75.0,
                "investor_ownership_pct": 20.0,
                "employee_pool_pct": 5.0,
            }
            if random.random() > 0.7:
                base["founder_ownership_pct"] = 72.5  # Vary stochastically
            return json.dumps(base)
        elif "safe" in prompt.lower() or "clause" in prompt.lower():
            base = {
                "has_pro_rata": True,
                "has_major_investor_consent": False,
                "has_acceleration": random.choice([True, False]),
            }
            return json.dumps(base)
        else:
            return "{}"
