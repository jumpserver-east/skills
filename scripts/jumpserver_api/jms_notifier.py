from __future__ import annotations

from typing import Any

import requests


def push_webhook(url: str, payload: dict[str, Any], *, timeout: int = 15) -> dict[str, Any]:
    target = str(url or "").strip()
    if not target:
        return {"sent": False, "reason": "empty_webhook_url"}
    try:
        response = requests.post(target, json=payload, timeout=timeout)
        return {
            "sent": response.ok,
            "status_code": response.status_code,
            "response_text": response.text[:500],
        }
    except Exception as exc:  # noqa: BLE001
        return {"sent": False, "reason": str(exc)}
