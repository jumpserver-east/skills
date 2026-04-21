---
name: jumpserver-runtime-setup
description: Use when users need JumpServer configuration, dependency bootstrap, connectivity checks, org selection, execution-context troubleshooting, or environment preflight before any other JumpServer workflow.
---

# JumpServer Runtime Setup

## Overview

这个子 skill 负责进入环境、确认当前组织上下文，并处理正式入口执行前的轻量排障。

## Use When

- 用户要生成或补齐 `.env`
- 用户要检查依赖、配置状态、连通性、当前组织或可访问组织
- 用户要显式切换组织，或解释 `candidate_orgs`、`switchable_orgs`
- 命令报“找不到脚本”、配置不完整、当前组织不可访问

不要用在对象详情、权限解释、审计调查或使用报告上。

## Primary Entrypoints

- `python3 jumpserver-runtime-setup/scripts/jms_diagnose.py config-status --json`
- `python3 jumpserver-runtime-setup/scripts/jms_diagnose.py config-write --payload '<json>' --confirm`
- `python3 jumpserver-runtime-setup/scripts/jms_diagnose.py ping`
- `python3 jumpserver-runtime-setup/scripts/jms_diagnose.py select-org --org-id <org-id> --confirm`

## Read These References

- [../references/runtime.md](../references/runtime.md)
- [../references/safety-rules.md](../references/safety-rules.md)
- [../references/troubleshooting.md](../references/troubleshooting.md)

## Guardrails

- 只允许本地运行时写入 `config-write --confirm` 和 `select-org --confirm`
- 若脚本路径报错，先检查 cwd 是否在仓库根目录，不要直接归因为文档路径错误
- 多组织且不能安全自动确定时，先阻塞并返回结构化组织提示