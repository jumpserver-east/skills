---
name: jumpserver-audit-investigation
description: Use when users need page-style JumpServer audit details for logins, sessions, commands, file transfers, jobs, or named-user login counts within a time window, rather than a report-style overview.
---

# JumpServer Audit Investigation

## Overview

这个子 skill 处理页面同款审计明细、调查型问题和命名用户登录次数统计。

## Use When

- 查登录日志、会话记录、命令记录、文件传输、作业列表
- 查某条会话详情、某天命令明细、最近审计记录
- 问一个或多个具体用户在某时间窗登录多少次

不要用在某天整体使用情况、日报、排行或 HTML 报告问题上。

## Primary Entrypoints

- `python3 jumpserver-audit-investigation/scripts/jms_query.py audit-list ...`
- `python3 jumpserver-audit-investigation/scripts/jms_query.py terminal-sessions ...`
- `python3 jumpserver-audit-investigation/scripts/jms_query.py job-list ...`
- `python3 jumpserver-audit-investigation/scripts/jms_query.py audit-analyze --capability ...`

## Read These References

- [../references/audit.md](../references/audit.md)
- [../references/routing-playbook.md](../references/routing-playbook.md)
- [../references/runtime.md](../references/runtime.md)

## Guardrails

- 命名用户登录次数优先 `audit-list --audit-type login`，直接引用 `summary.total`
- 不要把这类问题路由到 `daily-usage`、排行或 Top 榜单
- 非模板查询遇到相对时间词时，先固化为明确时间窗并在回答里回显