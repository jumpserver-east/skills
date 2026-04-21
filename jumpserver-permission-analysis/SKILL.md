---
name: jumpserver-permission-analysis
description: Use when users ask about JumpServer permission rules, ACL, RBAC, who is authorized to an asset, why a user can access an asset, or how an authorization rule applies.
---

# JumpServer Permission Analysis

## Overview

这个子 skill 处理授权主体、规则详情和访问依据解释，重点是“为什么”与“按什么规则”。

## Use When

- `为什么某人能访问某资产`
- `这条授权规则详情`
- `ACL`、`RBAC`、`权限详情`
- `这台资产授权给了谁`、`谁被授权到这台资产`

不要用在“某某用户有哪些资产”这类结果型访问范围问题上。

## Primary Entrypoints

- `python3 jumpserver-permission-analysis/scripts/jms_query.py asset-perm-users ...`
- `python3 jumpserver-permission-analysis/scripts/jms_query.py permission-list ...`
- `python3 jumpserver-permission-analysis/scripts/jms_query.py permission-get ...`
- `python3 jumpserver-permission-analysis/scripts/jms_diagnose.py asset-permission-explain ...`

## Read These References

- [../references/permissions.md](../references/permissions.md)
- [../references/diagnose.md](../references/diagnose.md)
- [../references/runtime.md](../references/runtime.md)

## Guardrails

- `资产授权给了谁` 默认回答授权主体，不默认把超级管理员混进来
- 若 `asset-perm-users` 为空，可再用 `asset-permission-explain` 核对规则命中
- 权限问题只读不写，不追加或移除关系