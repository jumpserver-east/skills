---
name: jumpserver-governance-inspection
description: Use when users ask for JumpServer governance inspection, capability-based aggregation, settings or license checks, tickets, storages, dashboards, component load, password-failure reporting, or other diagnose-and-inspect workflows beyond basic preflight.
---

# JumpServer Governance Inspection

## Overview

这个子 skill 处理治理巡检和 capability 聚合分析，侧重系统、资产、账号、组件和策略层面的检查。

## Use When

- `治理巡检`、`聚合分析`、`账号治理`、`资产治理`
- `系统设置`、`许可证`、`报表`、`dashboard`、`工单`
- `command storage`、`replay storage`、`terminal` 组件查询
- 组件负载概览、改密失败报错分析报表

不要把纯配置进入、组织切换和轻量排障放到这里；那属于 `jumpserver-runtime-setup`。

## Primary Entrypoints

- `python3 jumpserver-governance-inspection/scripts/jms_diagnose.py inspect --capability ...`
- `python3 jumpserver-governance-inspection/scripts/jms_diagnose.py reports ...`
- `python3 jumpserver-governance-inspection/scripts/jms_diagnose.py settings-category ...`
- `python3 jumpserver-governance-inspection/scripts/jms_diagnose.py tickets ...`

## Read These References

- [../references/diagnose.md](../references/diagnose.md)
- [../references/capabilities.md](../references/capabilities.md)
- [../references/component-load-and-password-report.md](../references/component-load-and-password-report.md)

## Guardrails

- 优先 capability，不手工拼多条零散查询
- 输出时明确区分治理概览、原始对象读取和统计结果三种口径
- 仍然遵守共享的只读边界和组织阻塞规则