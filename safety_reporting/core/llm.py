"""Thin client for the Lovable AI Gateway (OpenAI-compatible chat completions).

The only place in the system where a model is called. Streaming is used so long
generations do not sit behind a single silent round trip.
"""

from __future__ import annotations

import json
import os
import urllib.request

ENDPOINT = "https://ai.gateway.lovable.dev/v1/chat/completions"


class LLMError(RuntimeError):
    pass


def generate(system: str, user: str, model: str, temperature: float = 0.1) -> dict:
    key = os.environ.get("LOVABLE_API_KEY")
    if not key:
        raise LLMError("LOVABLE_API_KEY is not set")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "stream": True,
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
            "X-Lovable-AIG-SDK": "fetch",
        },
        method="POST",
    )
    chunks: list[str] = []
    try:
        with urllib.request.urlopen(req) as resp:
            run_id = resp.headers.get("X-Lovable-AIG-Run-ID")
            for raw in resp:
                line = raw.decode("utf-8").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    delta = json.loads(data)["choices"][0]["delta"].get("content")
                except (KeyError, IndexError, json.JSONDecodeError):
                    continue
                if delta:
                    chunks.append(delta)
    except urllib.error.HTTPError as exc:  # noqa: F821
        raise LLMError(f"gateway {exc.code}: {exc.read().decode()[:400]}") from exc

    text = "".join(chunks).strip()
    if not text:
        raise LLMError("model returned empty text")
    return {"text": text, "model": model, "run_id": run_id}
