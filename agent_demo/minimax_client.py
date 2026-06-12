import json
import os
import urllib.error
import urllib.request


class MiniMaxClient:
    def __init__(self):
        self.api_key = os.getenv("MINIMAX_API_KEY", "").strip()
        self.base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1").rstrip("/")
        self.model = os.getenv("MINIMAX_MODEL", "MiniMax-M1").strip()
        self.timeout = int(os.getenv("MINIMAX_TIMEOUT", "60"))

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: list[dict], temperature: float = 0.2) -> str:
        if not self.enabled:
            raise RuntimeError("MINIMAX_API_KEY is not set.")

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"MiniMax HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"MiniMax request failed: {exc.reason}") from exc

        result = json.loads(body)
        try:
            content = result["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected MiniMax response shape: {body[:500]}") from exc

        if content is None:
            raise RuntimeError(f"MiniMax returned null content: {body[:500]}")

        return str(content)
