# jumpserver-skills

`jumpserver-skills` 是一个面向 JumpServer V4 的查询型 skill 仓库。它现在支持环境初始化写入，包括根据用户回复生成 `.env.local`、持久化 `JMS_ORG_ID`，但资产、权限、审计相关业务动作仍然只保留查询。

[English](./README.en.md)

## 项目概览

| 入口 | 作用 | 当前范围 |
|---|---|---|
| `scripts/jms_assets.py` | 资产、账号、用户、用户组、平台、节点、组织查询 | `list`、`get` |
| `scripts/jms_permissions.py` | 授权规则查询 | `list`、`get` |
| `scripts/jms_audit.py` | 登录、操作、会话、命令审计 | `list`、`get` |
| `scripts/jms_diagnose.py` | 配置检查、配置写入、连通性、组织选择、对象解析、访问分析 | 环境初始化 + 只读诊断 |

## 核心规则

- 先执行 `python3 scripts/jms_diagnose.py config-status --json`
- 配置不完整时，按用户提供的信息执行 `python3 scripts/jms_diagnose.py config-write --payload '<json>' --confirm`
- 再执行 `python3 scripts/jms_diagnose.py ping`
- 缺少组织上下文时，执行 `python3 scripts/jms_diagnose.py select-org --org-id <org-id> --confirm`
- 只有 `{0002}` 或 `{0002,0004}` 两种保留组织集合才会自动写入 `0002`
- 不支持业务对象和权限的 `create/update/delete/append/remove/unblock`

## 快速开始

安装依赖：

```bash
python3 -m pip install -r requirements.txt
```

检查与初始化环境：

```bash
python3 scripts/jms_diagnose.py config-status --json
python3 scripts/jms_diagnose.py config-write --payload '{"JMS_API_URL":"https://jump.example.com","JMS_ACCESS_KEY_ID":"<ak>","JMS_ACCESS_KEY_SECRET":"<sk>","JMS_VERSION":"4"}' --confirm
python3 scripts/jms_diagnose.py ping
```

查看和写入组织：

```bash
python3 scripts/jms_diagnose.py select-org
python3 scripts/jms_diagnose.py select-org --org-id <org-id>
python3 scripts/jms_diagnose.py select-org --org-id <org-id> --confirm
```

之后再执行查询，例如：

```bash
python3 scripts/jms_assets.py list --resource user --filters '{"username":"demo-user"}'
python3 scripts/jms_permissions.py list --filters '{"limit":20}'
python3 scripts/jms_audit.py list --audit-type operate --filters '{"limit":30}'
```

## 常用命令

对象查询：

```bash
python3 scripts/jms_assets.py list --resource asset --filters '{"name":"demo-asset"}'
python3 scripts/jms_assets.py get --resource user --id <user-id>
python3 scripts/jms_diagnose.py resolve --resource node --name demo-node
python3 scripts/jms_diagnose.py resolve-platform --value Linux
```

访问分析：

```bash
python3 scripts/jms_diagnose.py user-assets --username demo-user
python3 scripts/jms_diagnose.py user-nodes --username demo-user
python3 scripts/jms_diagnose.py user-asset-access --username demo-user --asset-name demo-asset
```

审计查询：

```bash
python3 scripts/jms_audit.py list --audit-type login --filters '{"limit":10}'
python3 scripts/jms_audit.py get --audit-type command --id <command-id> --filters '{"command_storage_id":"<command-storage-id>"}'
```

## 环境模型

| 变量 | 说明 |
|---|---|
| `JMS_API_URL` 或 `JMS_WEB_URL` | JumpServer 地址 |
| `JMS_ACCESS_KEY_ID` + `JMS_ACCESS_KEY_SECRET` | AK/SK 鉴权 |
| `JMS_USERNAME` + `JMS_PASSWORD` | 基础鉴权 |
| `JMS_ORG_ID` | 当前查询组织 |
| `JMS_VERSION` | 默认 `4` |
| `JMS_TIMEOUT` | 可选超时 |

说明：

- 仓库支持通过 `config-write --confirm` 生成或更新 `.env.local`
- 仓库支持通过 `select-org --confirm` 写回 `JMS_ORG_ID`
- 正式业务命令仍然只保留查询能力

## 文档地图

| 文件 | 用途 |
|---|---|
| `SKILL.md` | 路由规则、环境初始化边界、查询边界 |
| `references/runtime.md` | 环境检查、`.env.local` 写入、组织持久化 |
| `references/assets.md` | 资产类查询 |
| `references/permissions.md` | 权限查询 |
| `references/audit.md` | 审计查询 |
| `references/diagnose.md` | 配置/组织/解析/访问分析 |
| `references/safety-rules.md` | 允许的环境写入与禁止的业务写入 |
| `references/troubleshooting.md` | 常见错误排查 |

## 不支持范围

- 资产、平台、节点、账号、用户、用户组、组织的创建/更新/删除/解锁
- 权限创建、更新、追加关系、移除关系、删除
- 临时 SDK/HTTP 脚本绕过正式流程
