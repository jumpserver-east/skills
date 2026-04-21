---
name: jumpserver-object-query
description: Use when users want to find or inspect JumpServer assets, accounts, account templates, users, user groups, orgs, platforms, nodes, labels, zones, or related object details without asking about permissions, audits, or usage reports.
---

# JumpServer Object Query

## Overview

这个子 skill 处理只读对象查询，重点是“对象是什么”和“对象详情是什么”，不是“谁能访问”或“为什么能访问”。

## Use When

- 查资产、账号、账号模板、用户、用户组、组织、平台、节点、标签、网域
- 按名称、地址、平台、节点、关键字查对象列表
- 读取单个对象详情或精确清单

不要用在用户有效访问范围、权限关系、审计调查或模板报告上。

## Primary Entrypoints

- `python3 jumpserver-object-query/scripts/jms_query.py object-list ...`
- `python3 jumpserver-object-query/scripts/jms_query.py object-get ...`

优先显式参数，例如 `--resource`、`--name`、`--kind`；低频字段再用 `--filter key=value`。

## Read These References

- [../references/assets.md](../references/assets.md)
- [../references/object-map.md](../references/object-map.md)
- [../references/runtime.md](../references/runtime.md)

## Guardrails

- 名称重名、平台不明确或跨组织命中时先阻塞，不猜对象
- `asset --kind` 只在资产资源下使用
- 用户问“有哪些资产能访问”时应切到 `jumpserver-effective-access`