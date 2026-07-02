"""
Location: projects/AI-PM/Knowledge/probe/models.py
Purpose: LLM client abstraction (DeepSeek hosted + Gemini hosted + Ollama local) with one interface
Functions: DeepSeekClient.generate(), GeminiClient.generate(), OllamaClient.generate()
Calls: (urllib.request, json)
Imports: urllib.request, json, os, abc
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
        req = urllib.request.Request(
            self.base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        last_error = None
        for attempt in range(1, self._MAX_ATTEMPTS + 1):
            try:
                # Reasoning models (v4-flash) think longer on compute tasks — 30s was too tight
                # (cap_table timed out); 120s gives headroom without hanging the bulk run.
                with urllib.request.urlopen(req, timeout=120) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                    return result["choices"][0]["message"]["content"]
            except urllib.error.HTTPError as e:
                last_error = e
                if e.code not in self._RETRYABLE_HTTP_CODES or attempt == self._MAX_ATTEMPTS:
                    raise RuntimeError(f"DeepSeek generation failed: HTTP Error {e.code}: {e.reason}")
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                # Network-level failure (DNS, connection reset, socket timeout) -- also transient.
                last_error = e
                if attempt == self._MAX_ATTEMPTS:
                    raise RuntimeError(f"DeepSeek generation failed: {e}")
            except Exception as e:
                # Anything else (bad JSON in the response body, unexpected shape, etc.) is NOT a
                # transient condition -- fail immediately rather than retrying blindly.
                raise RuntimeError(f"DeepSeek generation failed: {e}")
            time.sleep(self._BACKOFF_BASE_SECONDS * attempt)
        # Unreachable in practice (the loop always returns or raises), but keeps the fail-closed
        # contract explicit if _MAX_ATTEMPTS were ever set to 0.
        raise RuntimeError(f"DeepSeek generation failed after {self._MAX_ATTEMPTS} attempts: {last_error}")


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


class OllamaClient(LLMClient):
    """Local Ollama client (gemma4:12b)."""

    def __init__(self, model: str = "gemma4:12b", base_url: str = "http://localhost:11434"):
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
