---
name: jumpserver-effective-access
description: Use when users ask what assets, nodes, accounts, or protocols a specific JumpServer user can actually access now, especially for result-style questions like 有哪些资产、有哪些节点、有哪些账号 or which assets can this user access.
---

# JumpServer Effective Access

## Overview

这个子 skill 只回答用户当前“实际能访问什么”，不把结果型问法退回成授权规则说明。

## Use When

- `某某用户有哪些资产`
- `某某用户在 Default 组织下有哪些资产`
- `某某用户有哪些节点`
- `某某用户在某资产下有哪些账号 / 协议`

不要用在“为什么能访问”“权限详情”“授权给了谁”这类原因型问题上。

## Primary Entrypoints

- `python3 jumpserver-effective-access/scripts/jms_diagnose.py user-assets ...`
- `python3 jumpserver-effective-access/scripts/jms_diagnose.py user-nodes ...`
- `python3 jumpserver-effective-access/scripts/jms_diagnose.py user-asset-access ...`

## Read These References

- [../references/diagnose.md](../references/diagnose.md)
- [../references/runtime.md](../references/runtime.md)
- [../references/object-map.md](../references/object-map.md)

## Guardrails

- 用户显式给组织时，优先在单次命令内使用 `--org-id` 或 `--org-name` 限定组织
- 返回 `asset_count + assets`、`node_count + nodes`、或 `permed_accounts + permed_protocols`
- 不要把结果型问题自动翻译成授权依据解释