from __future__ import annotations

from collections import defaultdict
import re
from typing import Any

from .jms_ai_provider import analyze_session_with_ai
from .jms_analytics import _extract_asset, _extract_datetime, _extract_user, _first_field, _string_value


RISK_RULES = {
    "destructive": {
        "score": 35,
        "patterns": [
            r"\brm\s+-rf\b",
            r"\bdd\s+if=",
            r"\bmkfs\b",
            r"\bshutdown\b",
            r"\breboot\b",
        ],
    },
    "privilege_escalation": {
        "score": 25,
        "patterns": [
            r"\bsudo\b",
            r"\bsu\s+-\b",
            r"\bchmod\s+777\b",
            r"\bsetenforce\s+0\b",
        ],
    },
    "exfiltration": {
        "score": 20,
        "patterns": [
            r"\bcurl\b",
            r"\bwget\b",
            r"\bscp\b",
            r"\brsync\b",
            r"\bnc\b",
        ],
    },
    "credential_access": {
        "score": 20,
        "patterns": [
            r"/etc/passwd",
            r"/etc/shadow",
            r"id_rsa",
            r"authorized_keys",
        ],
    },
}

RISK_TYPE_LABELS = {
    "destructive": "破坏性操作",
    "privilege_escalation": "权限提升",
    "exfiltration": "数据外传",
    "credential_access": "凭据访问",
}


def _command_text(record: dict[str, Any]) -> str:
    return str(_first_field(record, "command", "command_text", "input", "cmd") or "").strip()


def _session_id(record: dict[str, Any]) -> str:
    value = str(_first_field(record, "session", "session_id") or "").strip()
    if value:
        return value
    user = _extract_user(record) or "unknown"
    asset = _extract_asset(record) or "unknown"
    return "fallback:%s:%s" % (user, asset)


def _risk_from_command(command: str) -> tuple[int, list[str], list[str]]:
    score = 0
    factors: list[str] = []
    matched_terms: list[str] = []
    lowered = command.lower()
    for rule_name, rule in RISK_RULES.items():
        for pattern in rule["patterns"]:
            match = re.search(pattern, lowered)
            if match:
                score += int(rule["score"])
                factors.append(rule_name)
                term = str(match.group(0) or "").strip()
                if term and term not in matched_terms:
                    matched_terms.append(term)
                break
    return score, factors, matched_terms


def _short_text(value: str, *, limit: int = 120) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: max(limit - 3, 0)] + "..."


def _sequence_bonus(unique_factors: set[str], risky_command_count: int) -> tuple[int, list[str]]:
    bonus = 0
    reasons: list[str] = []
    if "privilege_escalation" in unique_factors and "destructive" in unique_factors:
        bonus += 20
        reasons.append("提权后破坏命令链")
    if "credential_access" in unique_factors and "exfiltration" in unique_factors:
        bonus += 15
        reasons.append("凭据访问后外传链路")
    if risky_command_count >= 5:
        bonus += 10
        reasons.append("高频风险命令爆发")
    return bonus, reasons


def _risk_level(score: int) -> str:
    if score >= 80:
        return "高"
    if score >= 45:
        return "中"
    return "低"


def analyze_risky_sessions(
    command_records: list[dict[str, Any]],
    *,
    max_sessions: int = 10,
) -> dict[str, Any]:
    by_session: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in command_records:
        by_session[_session_id(record)].append(record)

    risky_rows: list[dict[str, Any]] = []
    for sid, rows in by_session.items():
        ordered = sorted(rows, key=lambda item: _extract_datetime(item) or 0)
        total_score = 0
        factor_counts: dict[str, int] = defaultdict(int)
        risky_commands: list[str] = []
        rule_hits: list[str] = []

        for item in ordered:
            command = _command_text(item)
            if not command:
                continue
            score, factors, matched_terms = _risk_from_command(command)
            total_score += score
            for factor in factors:
                factor_counts[factor] += 1
                rule_hits.append("%s:%s" % (factor, command[:60]))
            if score > 0:
                risky_commands.append(command)

        if not risky_commands:
            continue

        base_score = total_score
        chain_bonus = 15 if len(risky_commands) >= 3 else 0
        unique_factors = set(factor_counts.keys())
        seq_bonus, seq_reasons = _sequence_bonus(unique_factors, len(risky_commands))
        total_score += chain_bonus + seq_bonus

        user = _extract_user(ordered[0]) or "unknown"
        asset = _extract_asset(ordered[0]) or "unknown"
        factors_sorted = sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)
        factor_labels = ["%s(%s)" % (name, count) for name, count in factors_sorted[:4]]
        contexts = []
        for item in ordered:
            command = _command_text(item)
            if not command:
                continue
            _, factors, matched_terms = _risk_from_command(command)
            if not factors:
                continue
            contexts.append(
                {
                    "risk_types": factors,
                    "command": _short_text(command, limit=180),
                    "matched_terms": matched_terms,
                }
            )

        ai_payload = {
            "session_id": sid,
            "user": user,
            "asset": asset,
            "risk_score": total_score,
            "commands": risky_commands[:8],
            "factors": factor_labels,
        }
        ai_result = analyze_session_with_ai(ai_payload)
        command_brief = "、".join([_short_text(cmd, limit=28) for cmd in risky_commands[:2]]) or "敏感命令"
        risk_brief_labels = [RISK_TYPE_LABELS.get(name, name) for name in list(unique_factors)[:3]]
        risk_brief = "、".join(risk_brief_labels) if risk_brief_labels else "异常操作"
        analysis_text = "此会话调用了%s等命令，可能存在%s风险。" % (command_brief, risk_brief)
        ai_summary = str(ai_result.get("risk_summary") or "").strip()
        if ai_summary:
            analysis_text = "%s AI补充：%s" % (analysis_text, _short_text(ai_summary, limit=100))

        risky_rows.append(
            {
                "session_id": sid,
                "user": user,
                "asset": asset,
                "risk_score": total_score,
                "risk_level": _risk_level(total_score),
                "risk_factors": ", ".join(factor_labels) if factor_labels else "unknown",
                "risk_scoring_breakdown": "base=%s,chain_bonus=%s,sequence_bonus=%s" % (base_score, chain_bonus, seq_bonus),
                "risk_sequence_reasons": " / ".join(seq_reasons) if seq_reasons else "无额外序列信号",
                "rule_hits": rule_hits[:8],
                "matched_contexts": contexts[:8],
                "command_chain": " -> ".join(risky_commands[:5]),
                "analysis": analysis_text,
                "ai_used": bool(ai_result.get("ai_used")),
            }
        )

    risky_rows.sort(key=lambda item: int(item.get("risk_score") or 0), reverse=True)
    top_rows = risky_rows[: max(1, int(max_sessions or 10))]

    ai_used_count = sum(1 for item in top_rows if item.get("ai_used"))
    summary = (
        "共识别 %s 个可疑会话；Top 会话风险分 %s；其中 %s 个会话使用 AI 完成语义分析。"
        % (
            len(top_rows),
            int(top_rows[0].get("risk_score") or 0) if top_rows else 0,
            ai_used_count,
        )
    )

    return {
        "risk_session_total": len(top_rows),
        "risk_sessions": top_rows,
        "risk_session_summary": summary,
        "risk_scoring_notes": "评分=规则基线分+命令链加分+上下文序列加分；AI 仅用于语义解释，不覆盖规则判定。",
    }
