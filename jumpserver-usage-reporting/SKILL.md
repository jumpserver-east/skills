---
name: jumpserver-usage-reporting
description: Use when users ask for JumpServer usage reports, daily or time-range summaries, rankings, top lists, overviews, or what happened on a specific day or period, especially when the output should be an HTML report.
---

# JumpServer Usage Reporting

## Overview

这个子 skill 处理某一天或某时间段的 JumpServer 使用情况与模板报告，默认产出完整 HTML 报告。

## Use When

- `使用报告`、`日报`、`周报`、`月报`
- `某天使用情况`、`某时间段使用分析`
- `谁登录最多`、`哪些资产最活跃`、`某天发生了什么`
- 带时间词的整体情况、排行、TOP、概览

如果用户明确说“不要生成报告”“只给结论”“不用模板”，才允许降级为非模板分析。

## Primary Entrypoint

- `python3 jumpserver-usage-reporting/scripts/jms_report.py daily-usage ...`

## Read These References

- [../references/report-template-playbook.md](../references/report-template-playbook.md)
- [../references/routing-playbook.md](../references/routing-playbook.md)
- [../references/runtime.md](../references/runtime.md)

## Guardrails

- 先把 `昨天`、`上周`、`本月`、`20260310` 等表达归一化为明确时间窗
- 成功生成后必须先明确说明“报告已生成”，并回显产物与校验摘要
- 未显式给组织的报告请求优先尝试全局组织 `00000000-0000-0000-0000-000000000000`