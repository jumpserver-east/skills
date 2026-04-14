from __future__ import annotations

import json
import os
from typing import Any

import requests


DEFAULT_TIMEOUT_SECONDS = 20


def _env_bool(name: str, default: bool = False) -> bool:
    value = str(os.getenv(name, "")).strip().lower()
    if not value:
        return default
    return value in {"1", "true", "yes", "on", "y"}


def ai_enabled() -> bool:
    return _env_bool("JMS_AI_ENABLE", default=False)


def _build_prompt(payload: dict[str, Any]) -> list[dict[str, str]]:
    system_prompt = (
        "你是堡垒机审计分析助手。"
        "请根据会话内命令序列识别风险行为，返回简洁 JSON。"
        "只输出 JSON，不要输出多余文本。"
    )
    user_prompt = {
        "task": "analyze_risky_session",
        "input": payload,
        "output_schema": {
            "risk_summary": "string",
            "confidence": "number_between_0_and_1",
            "risk_factors": ["string"],
            "recommended_action": "string",
        },
    }
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)},
    ]


def analyze_session_with_ai(payload: dict[str, Any]) -> dict[str, Any]:
    if not ai_enabled():
        return {"ai_enabled": False, "ai_used": False}

    endpoint = str(os.getenv("JMS_AI_ENDPOINT", "")).strip()
    model = str(os.getenv("JMS_AI_MODEL", "")).strip()
    api_key = str(os.getenv("JMS_AI_API_KEY", "")).strip()
    timeout = int(str(os.getenv("JMS_AI_TIMEOUT", DEFAULT_TIMEOUT_SECONDS)).strip() or DEFAULT_TIMEOUT_SECONDS)

    if not endpoint or not model:
        return {
            "ai_enabled": True,
            "ai_used": False,
            "ai_error": "missing_endpoint_or_model",
        }

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer %s" % api_key

    request_payload = {
        "model": model,
        "temperature": 0.1,
        "messages": _build_prompt(payload),
    }

    try:
        response = requests.post(endpoint, headers=headers, json=request_payload, timeout=timeout)
        response.raise_for_status()
        body = response.json()
    except Exception as exc:  # noqa: BLE001
        return {
            "ai_enabled": True,
            "ai_used": False,
            "ai_error": str(exc),
        }

    content = (
        ((body.get("choices") or [{}])[0].get("message") or {}).get("content")
        if isinstance(body, dict)
        else None
    )
    if not content:
        return {
            "ai_enabled": True,
            "ai_used": False,
            "ai_error": "empty_ai_response",
        }

    try:
        parsed = json.loads(content)
    except Exception:  # noqa: BLE001
        return {
            "ai_enabled": True,
            "ai_used": True,
            "ai_parse_error": True,
            "raw_content": str(content),
        }

    if not isinstance(parsed, dict):
        return {
            "ai_enabled": True,
            "ai_used": True,
            "ai_parse_error": True,
            "raw_content": str(content),
        }

    return {
        "ai_enabled": True,
        "ai_used": True,
        "risk_summary": str(parsed.get("risk_summary") or "").strip(),
        "confidence": parsed.get("confidence"),
        "risk_factors": parsed.get("risk_factors") if isinstance(parsed.get("risk_factors"), list) else [],
        "recommended_action": str(parsed.get("recommended_action") or "").strip(),
    }
