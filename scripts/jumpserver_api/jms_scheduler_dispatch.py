from __future__ import annotations

from datetime import datetime
import re
import time
from typing import Any

from .jms_notifier import push_webhook
from .jms_reporting import build_daily_usage_report


SCHEDULE_FOR_CHOICES = {"daily", "weekly", "monthly"}
UUID_LIKE_RE = re.compile(
    r"^[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}$"
)


def _schedule_to_report_kwargs(schedule_for: str) -> dict[str, Any]:
    normalized = str(schedule_for or "").strip().lower()
    if normalized not in SCHEDULE_FOR_CHOICES:
        raise ValueError("Unsupported schedule_for: %s" % schedule_for)
    if normalized == "daily":
        return {"date_expr": "昨天"}
    if normalized == "weekly":
        return {"period_expr": "上周"}
    return {"period_expr": "本月"}


def _parse_org_list(org_list: list[str] | str | None) -> list[str]:
    if org_list is None:
        return []
    if isinstance(org_list, str):
        raw_items = org_list.split(",")
    elif isinstance(org_list, list):
        raw_items = [str(item) for item in org_list]
    else:
        raw_items = [str(org_list)]
    parsed: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        value = str(item or "").strip()
        if not value:
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        parsed.append(value)
    return parsed


def _build_targets(*, org_id: str | None, org_name: str | None, org_list: list[str]) -> list[dict[str, str]]:
    targets: list[dict[str, str]] = []
    if str(org_id or "").strip():
        targets.append({"org_id": str(org_id).strip()})
    if str(org_name or "").strip():
        targets.append({"org_name": str(org_name).strip()})
    for value in org_list:
        if UUID_LIKE_RE.fullmatch(value):
            targets.append({"org_id": value})
        else:
            targets.append({"org_name": value})
    if not targets:
        targets.append({})
    unique: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in targets:
        key = "org_id:%s" % item.get("org_id") if item.get("org_id") else "org_name:%s" % item.get("org_name")
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def _execute_with_retry(*, report_kwargs: dict[str, Any], retry_count: int, retry_delay_seconds: float) -> dict[str, Any]:
    attempts = max(int(retry_count or 0), 0) + 1
    errors: list[dict[str, Any]] = []
    for index in range(attempts):
        try:
            result = build_daily_usage_report(**report_kwargs)
            return {
                "ok": True,
                "attempt_count": index + 1,
                "result": result,
                "errors": errors,
            }
        except Exception as exc:  # noqa: BLE001
            errors.append({"attempt": index + 1, "error": str(exc)})
            if index >= attempts - 1:
                break
            if retry_delay_seconds > 0:
                time.sleep(float(retry_delay_seconds))
    return {
        "ok": False,
        "attempt_count": attempts,
        "errors": errors,
    }


def run_scheduled_report(
    *,
    schedule_for: str,
    org_id: str | None = None,
    org_name: str | None = None,
    org_list: list[str] | str | None = None,
    webhook_url: str | None = None,
    command_storage_id: str | None = None,
    retry_count: int = 1,
    retry_delay_seconds: float = 1.0,
    dry_run: bool = False,
) -> dict[str, Any]:
    report_kwargs = _schedule_to_report_kwargs(schedule_for)
    parsed_org_list = _parse_org_list(org_list)
    targets = _build_targets(org_id=org_id, org_name=org_name, org_list=parsed_org_list)

    if dry_run:
        return {
            "schedule_for": schedule_for,
            "dry_run": True,
            "target_count": len(targets),
            "targets": targets,
            "report_kwargs": {
                **report_kwargs,
                "command_storage_id": command_storage_id,
            },
            "retry_policy": {
                "retry_count": max(int(retry_count or 0), 0),
                "retry_delay_seconds": float(retry_delay_seconds or 0),
            },
            "webhook_enabled": bool(str(webhook_url or "").strip()),
        }

    reports: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for target in targets:
        target_kwargs = {
            **report_kwargs,
            "org_id": target.get("org_id"),
            "org_name": target.get("org_name"),
            "command_storage_id": command_storage_id,
        }
        execution = _execute_with_retry(
            report_kwargs=target_kwargs,
            retry_count=retry_count,
            retry_delay_seconds=retry_delay_seconds,
        )
        if execution.get("ok"):
            reports.append(
                {
                    "target": target,
                    "attempt_count": execution.get("attempt_count"),
                    "report": execution.get("result"),
                }
            )
            continue
        failures.append(
            {
                "target": target,
                "attempt_count": execution.get("attempt_count"),
                "errors": execution.get("errors") or [],
            }
        )

    push_result = None
    if webhook_url:
        payload = {
            "event": "jumpserver_report_generated",
            "schedule_for": schedule_for,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "success_count": len(reports),
                "failed_count": len(failures),
                "target_count": len(targets),
            },
            "reports": [
                {
                    "target": item.get("target"),
                    "output_path": ((item.get("report") or {}).get("output_path")),
                    "report_date": ((item.get("report") or {}).get("report_date")),
                    "date_from": ((item.get("report") or {}).get("date_from")),
                    "date_to": ((item.get("report") or {}).get("date_to")),
                    "effective_org": ((item.get("report") or {}).get("effective_org")),
                }
                for item in reports
            ],
            "failures": failures,
        }
        push_result = push_webhook(str(webhook_url), payload)

    response: dict[str, Any] = {
        "schedule_for": schedule_for,
        "dry_run": False,
        "target_count": len(targets),
        "reports": reports,
        "failures": failures,
        "summary": {
            "success_count": len(reports),
            "failed_count": len(failures),
            "target_count": len(targets),
        },
        "retry_policy": {
            "retry_count": max(int(retry_count or 0), 0),
            "retry_delay_seconds": float(retry_delay_seconds or 0),
        },
        "webhook": push_result,
    }
    if len(reports) == 1 and not failures:
        response["report"] = reports[0].get("report")
    return response
