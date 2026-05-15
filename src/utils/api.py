"""DeepSeek API wrapper for APIFlow -- thin client around httpx + OpenAI-compatible API."""

import os
import json
from dataclasses import dataclass, field
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()


@dataclass
class APIFlowConfig:
    """Configuration loaded from environment variables."""
    api_key: str = ""
    base_url: str = "https://api.deepseek.com/v1"
    model: str = "deepseek-chat"
    temperature: float = 0.3
    max_tokens: int = 4096
    timeout: float = 120.0

    @classmethod
    def from_env(cls) -> "APIFlowConfig":
        return cls(
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            model=os.getenv("APIFLOW_MODEL", os.getenv("DEEPSEEK_MODEL", "deepseek-chat")),
        )

    def validate(self):
        if not self.api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY not set. "
                "Export it or create a .env file based on .env.example."
            )


class DeepSeekClient:
    """Lightweight wrapper over httpx targeting the DeepSeek (OpenAI-compatible) API."""

    def __init__(self, config: Optional[APIFlowConfig] = None):
        self.config = config or APIFlowConfig.from_env()
        self.config.validate()
        self._base_url = self.config.base_url.rstrip("/")

    # -- public interface ---------------------------------------------------

    def chat(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Send a single chat completion request and return the assistant text."""
        url = f"{self._base_url}/chat/completions"
        payload = {
            "model": self.config.model,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=self.config.timeout) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"] or ""

    def chat_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> dict:
        """Send a chat completion and parse the response as JSON.

        Automatically appends a JSON-only instruction to the system prompt,
        strips markdown fences, and falls back gracefully on parse errors.
        """
        json_prompt = (
            system_prompt
            + "\n\nYou MUST respond with valid JSON only. "
            "No markdown fences, no extra text, no explanation."
        )
        text = self.chat(
            json_prompt,
            user_message,
            temperature=temperature if temperature is not None else 0.1,
            max_tokens=max_tokens,
        )
        text = text.strip()
        # strip markdown code fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            lines = lines[1:] if lines[0].startswith("```") else lines
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text, "error": "Failed to parse as JSON"}
