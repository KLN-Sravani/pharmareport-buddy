"""Thin client for the Lovable AI Gateway (OpenAI-compatible chat completions).

The only place in the system where a model is called. Streaming is used so a
long generation does not sit behind one silent round trip.
"""

from __future__ import annotations

import json
import os

import requests

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
    resp = requests.post(
        ENDPOINT,
        json=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "X-Lovable-AIG-SDK": "fetch",
        },
        stream=True,
    )
    if resp.status_code != 200:
        raise LLMError(f"gateway {resp.status_code}: {resp.text[:400]}")

    run_id = resp.headers.get("X-Lovable-AIG-Run-ID")
    chunks: list[str] = []
    for raw in resp.iter_lines(decode_unicode=True):
        if not raw or not raw.startswith("data:"):
            continue
        data = raw[5:].strip()
        if data == "[DONE]":
            break
        try:
            delta = json.loads(data)["choices"][0]["delta"].get("content")
        except (KeyError, IndexError, json.JSONDecodeError):
            continue
        if delta:
            chunks.append(delta)

    text = "".join(chunks).strip()
    if not text:
        raise LLMError("model returned empty text")
    return {"text": text, "model": model, "run_id": run_id}
