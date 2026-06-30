"""
Location: projects/AI-PM/Knowledge/probe/models.py
Purpose: LLM client abstraction (DeepSeek hosted + Gemini hosted + Ollama local) with one interface
Functions: DeepSeekClient.generate(), GeminiClient.generate(), OllamaClient.generate()
Calls: (urllib.request, json)
Imports: urllib.request, json, os, abc
"""

import urllib.request
import json
import os
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

    def generate(self, prompt: str, temperature: float) -> str:
        """Generate via DeepSeek. Assert temp > 0 (SP1)."""
        if temperature <= 0:
            raise ValueError(f"Temperature must be >0 (got {temperature}). SP1: no determinism.")

        try:
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

            # Reasoning models (v4-flash) think longer on compute tasks — 30s was too tight
            # (cap_table timed out); 120s gives headroom without hanging the bulk run.
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            raise RuntimeError(f"DeepSeek generation failed: {e}")


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

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "gemma4:12b"

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
