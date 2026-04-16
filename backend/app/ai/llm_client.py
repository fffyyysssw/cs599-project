from __future__ import annotations

import json
import re
from typing import Any

import httpx

from app.core.config import get_settings


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def enabled(self) -> bool:
        return bool(self.settings.llm_api_key.strip())

    def chat_json(self, prompt: str) -> dict[str, Any]:
        if not self.enabled:
            raise RuntimeError("LLM 未启用")

        base_url = self.settings.llm_base_url.rstrip("/")
        payload = {
            "model": self.settings.llm_model,
            "messages": [
                {"role": "system", "content": "你是一个只返回 JSON 的企业审批助手。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        headers = {"Authorization": f"Bearer {self.settings.llm_api_key}"}
        with httpx.Client(timeout=30) as client:
            response = client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        return self._extract_json(content)

    def _extract_json(self, text: str) -> dict[str, Any]:
        fence_match = re.search(r"```json\s*(\{.*\})\s*```", text, flags=re.S)
        raw = fence_match.group(1) if fence_match else text
        raw = raw.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\})", raw, flags=re.S)
            if not match:
                raise
            return json.loads(match.group(1))
