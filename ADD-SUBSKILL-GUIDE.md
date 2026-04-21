# 新增子 Skill 指南

这份文档说明后续如何在当前仓库里继续新增一个按用户意图拆分的 JumpServer 子 skill，并保持和现有架构一致。

当前仓库已经固定为下面这套结构：

- 根目录保留总路由 skill
- 每个子 skill 负责一个清晰的用户意图边界
- 对外正式入口只暴露在各子 skill 自己的 `scripts/*.py`
- 共享实现只放在根目录 [jumpserver-api](./jumpserver-api)
- `jumpserver-api` 现在必须保持单层目录，不再允许出现 `jumpserver-api/jumpserver_api` 这种两层结构

## 先判断要不要拆新子 skill

先判断是不是“真的需要新增一个子 skill”，而不是只是在现有子 skill 里补一个命令。

适合新增子 skill 的情况：

- 用户意图已经形成稳定边界，例如“对象查询”“有效访问范围”“权限解释”“审计调查”“治理巡检”这种级别
- 这一类请求有自己独立的路由判断规则
- 这一类请求适合被单独注册成 skill 根目录
- 这一类请求需要自己的 `SKILL.md`、接入描述和本地正式入口

不适合新增子 skill 的情况：

- 只是现有子 skill 下面多一个查询命令
- 只是补一个 capability 或报表类型
- 只是复用现有 `jms_query.py` / `jms_diagnose.py` 的一个小分支
- 只是共享底层逻辑扩展，不涉及新的用户意图边界

简单判断原则：

- 如果用户先要区分“这类问题应该路由到哪里”，适合新建子 skill
- 如果只是“同一类问题里新增一个能力”，优先放进已有子 skill

## 命名与目录约定

新增子 skill 时，目录名统一使用：

```text
jumpserver-<intent-name>
```

要求：

- 用英文小写和连字符
- 名称直接表达用户意图，不表达技术实现
- 不要把共享层、公共层、core、common 之类概念做成新的子 skill 名

新增目录的最小结构如下：

```text
jumpserver-<intent-name>/
  SKILL.md
  agents/
    openai.yaml
  scripts/
    jms_query.py        # 按需
    jms_diagnose.py     # 按需
    jms_report.py       # 按需
```

说明：

- 子 skill 不要求一定同时拥有三种入口
- 只创建这个子 skill 真正需要暴露的本地正式入口
- 不要在子 skill 里复制一份共享运行时

## 新子 Skill 的必改位置

新增一个子 skill，通常至少会改这些位置：

### 1. 新建子 skill 自身目录

- `jumpserver-<intent-name>/SKILL.md`
- `jumpserver-<intent-name>/agents/openai.yaml`
- `jumpserver-<intent-name>/scripts/*.py`

### 2. 更新根目录路由与说明

- [README.md](./README.md)
- [README.en.md](./README.en.md)
- [SKILL.md](./SKILL.md)
- [agents/openai.yaml](./agents/openai.yaml)

### 3. 如果新增了新 profile 或新命令集合，更新共享入口

按实际需要修改：

- [jumpserver-api/jms_query.py](./jumpserver-api/jms_query.py)
- [jumpserver-api/jms_diagnose.py](./jumpserver-api/jms_diagnose.py)
- [jumpserver-api/jms_report.py](./jumpserver-api/jms_report.py)
- [jumpserver-api/jms_runtime.py](./jumpserver-api/jms_runtime.py)

### 4. 如果新增 capability 或元数据映射，更新共享元数据

按实际需要修改：

- [references/metadata/capabilities.json](./references/metadata/capabilities.json)
- [references/capabilities.md](./references/capabilities.md)
- 相关引用文档，例如 `routing-playbook`、`runtime`、`diagnose`、`audit`、`permissions`

## SKILL.md 怎么写

子 skill 的 [SKILL.md](./SKILL.md) 继续沿用当前仓库已经稳定下来的结构：

```md
---
name: jumpserver-<intent-name>
description: Use when ...
---

# JumpServer <Title>

## Overview

一句话说明这个子 skill 解决什么问题。

## Use When

- 列出 3 到 6 条典型用户问法
- 明确哪些问题不归这个子 skill 管

## Primary Entrypoints

- `python3 jumpserver-<intent-name>/scripts/jms_query.py ...`
- `python3 jumpserver-<intent-name>/scripts/jms_diagnose.py ...`

## Read These References

- 指向根目录 `references/` 中真正相关的文档

## Guardrails

- 只写这个子 skill 特有的边界和禁区
```

写法要求：

- frontmatter 里的 `name` 用目录名
- `description` 只写“什么时候用”，不要写“内部怎么做”
- `Primary Entrypoints` 只写这个子 skill 自己的本地入口，不写 `jumpserver-api/*.py`
- `Guardrails` 只写本子 skill 独有的边界，不重复整个仓库的公共规则

## agents/openai.yaml 怎么写

每个子 skill 都应该能被单独注册，所以要提供自己的接入描述。

最小模板可以按现有子 skill 的写法复制：

```yaml
interface:
  display_name: "JumpServer <Title>"
  short_description: "JumpServer V4.10 单 skill 接入描述。适用于……"
  default_prompt: |
    使用 $jumpserver-<intent-name> 处理 JumpServer V4.10 ……问题。
    当这个子目录被单独注册为 skill 根目录时，优先使用本地入口：
    - `python3 scripts/jms_query.py ...`
    - `python3 scripts/jms_diagnose.py ...`
    这些本地入口会从仓库根目录加载共享底层 `jumpserver-api/...`；如果共享目录不存在，说明当前 skill 包不完整。
```

要求：

- 明确这个子 skill 处理哪类请求
- 列出它自己的本地入口，而不是仓库根目录入口
- 明确说明共享实现位于 `jumpserver-api/`

## scripts 本地入口怎么写

所有子 skill 的 `scripts/*.py` 都应该是“本地正式入口”，但它本身保持很薄，只负责：

- 计算仓库根目录
- 检查 `jumpserver-api/` 是否存在
- 把 `jumpserver-api/` 插入 `sys.path`
- 动态导入共享入口模块
- 设置本子 skill 的本地入口覆盖路径
- 调用对应 profile

典型模板如下：

```python
#!/usr/bin/env python3
from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
JUMPSERVER_API_ROOT = REPO_ROOT / "jumpserver-api"
LOCAL_ENTRYPOINT = "jumpserver-<intent-name>/scripts/jms_diagnose.py"


if __name__ == "__main__":
    if not JUMPSERVER_API_ROOT.exists():
        raise SystemExit(
            "Missing jumpserver-api directory: %s. Register this subskill from the full repository checkout."
            % JUMPSERVER_API_ROOT
        )
    sys.path.insert(0, str(JUMPSERVER_API_ROOT))

    diagnose_module = import_module("jms_diagnose")
    runtime_module = import_module("jms_runtime")

    runtime_module.set_entrypoint_override("jms_diagnose.py", LOCAL_ENTRYPOINT)
    raise SystemExit(diagnose_module.main(profile="<intent-name>"))
```

注意：

- `import_module()` 里现在直接导入顶层模块名，例如 `jms_query`、`jms_diagnose`
- 不要再写成 `jumpserver_api.jms_query`
- `jumpserver-api` 必须是一层目录，不能再套内层 Python 包目录
- `LOCAL_ENTRYPOINT` 必须写当前子 skill 自己的相对路径

## 共享代码放哪里

共享代码只允许放在根目录 [jumpserver-api](./jumpserver-api) 下，并且只放“中性、可复用、和具体子 skill 无关”的实现。

适合放共享层的内容：

- API client
- 运行时与组织上下文
- discovery
- analytics
- reporting
- capability 元数据装载
- 被多个子 skill 共用的 query / diagnose / report 正式入口

不适合放共享层的内容：

- 某个子 skill 私有的路由说明
- 某个子 skill 特有的高层文案
- 只服务某一个子 skill 的目录结构约定

也不要把共享代码放回某个子 skill 目录里充当“宿主”，例如：

- 不要重新出现 `jumpserver-runtime-setup/scripts/jumpserver_api/`
- 不要创建新的 `shared-core/`
- 不要创建 `jumpserver-api/jumpserver_api/`

## 什么时候要改 jms_query / jms_diagnose / jms_report

如果新子 skill 只是复用现有 profile，不一定要改共享入口。

只有在下面这些情况下才需要改：

- 需要新增一个新的 profile 名称
- 需要给这个子 skill 暴露一组新的命令子集
- 需要新增新的 usage examples
- 需要新增新的 capability 入口
- 需要修正 `suggested_commands` 或帮助文本中的路径

常见改法：

- 在 `*_PROFILE_SETTINGS` 里增加一个 profile
- 把 profile 绑定到正确的 commands 集合
- 给新命令补 usage examples
- 确保帮助文本和推荐命令使用子 skill 本地入口路径

## 文档更新顺序

建议按这个顺序更新文档，避免路由和实现脱节：

1. 先写新子 skill 的 `SKILL.md`
2. 再写它自己的 `agents/openai.yaml`
3. 再补根目录总路由说明
4. 再补 README 中的子 skill 列表和边界说明
5. 最后补相关 `references/` 文档和 metadata

## 新增后的验证清单

新增子 skill 后，至少做这几项验证：

### 1. 入口帮助检查

直接执行本地入口：

```bash
python3 jumpserver-<intent-name>/scripts/jms_query.py --help
python3 jumpserver-<intent-name>/scripts/jms_diagnose.py --help
python3 jumpserver-<intent-name>/scripts/jms_report.py --help
```

只跑这个子 skill 真正存在的入口。

### 2. 文本残留检查

确认没有这些残留：

- `jumpserver-api/jumpserver_api`
- `jumpserver_api.`
- 旧 wrapper / runpy 转发痕迹
- 旧的集中式路径描述

### 3. 编辑器诊断

确认新加脚本和共享模块没有新的诊断错误。

### 4. 根目录路由检查

确认下面四处都知道这个新子 skill：

- 根目录 [README.md](./README.md)
- 根目录 [README.en.md](./README.en.md)
- 根目录 [SKILL.md](./SKILL.md)
- 根目录 [agents/openai.yaml](./agents/openai.yaml)

## 推荐的最小交付标准

一个新的子 skill，至少满足下面这些条件再算完成：

- 已有独立目录 `jumpserver-<intent-name>/`
- 已有自己的 `SKILL.md`
- 已有自己的 `agents/openai.yaml`
- 已有自己的本地 `scripts/*.py` 正式入口
- 根目录路由文档已经认识它
- 如果需要 profile，`jumpserver-api/*.py` 已完成注册
- `--help` 验证通过

## 一句话原则

新增子 skill 时，优先新增“用户意图边界”和“本地正式入口”；共享实现仍然只保留一份，继续收敛在根目录 [jumpserver-api](./jumpserver-api) 这一层。