# SSH 向导连接 (SSH Guide Connection) 说明文档

## 概述

SSH 向导连接是堡垒机提供的一种便捷的远程连接方式。该文档说明如何在 JumpServer skills 项目中使用 SSH 向导连接功能获取临时连接令牌。

## 功能特性

✨ **核心特性**：
- 通过资产名称、IP 地址或 UUID 自动查询和解析资产
- 通过账号名称、用户名或 UUID 自动查询和解析账号
- 获取临时连接令牌（用户名和密码）
- 支持多种连接协议（SSH、RDP、VNC、数据库等）
- 完整的错误处理和提示

## 功能说明

### 什么是 SSH 向导连接？

SSH 向导连接是堡垒机中一种简化的连接流程：
1. 用户选择要连接的资产（主机）
2. 选择要使用的账号（用户/密钥）
3. 选择连接协议（SSH、RDP、VNC 等）
4. 堡垒机返回一个临时的连接令牌
5. 使用这个令牌连接到目标资产

### 核心 API 端点

```
POST /api/v1/authentication/connection-token/
```

**功能**: 获取用于 SSH 向导连接的临时令牌。

**请求负载示例**:
```json
{
  "asset": "2fcc289b-f985-4e51-bde9-65d63bf47cca",
  "account": "fb13bca0-6136-4d83-9bc0-6de7087d99fd",
  "protocol": "ssh",
  "input_username": "root",
  "input_secret": "",
  "connect_method": "ssh_guide",
  "connect_options": {
    "charset": "default",
    "disableautohash": false,
    "token_reusable": false,
    "resolution": "auto",
    "backspaceAsCtrlH": false,
    "appletConnectMethod": "web",
    "virtualappConnectMethod": "web",
    "reusable": false,
    "rdp_connection_speed": "auto"
  }
}
```

**响应示例**:
```json
{
  "id": "username_for_connection",
  "value": "temporary_token_password"
}
```

其中：
- `id`: 用作 SSH 连接的用户名
- `value`: 用作 SSH 连接的密码（临时令牌）

## 模块结构

### 1. Core Module: `jms_ssh_guide.py`

核心模块，不能作为独立脚本运行，需要被导入使用。

#### 类和函数

##### `SSHGuideConnector` 类

主要的连接器类，处理与堡垒机的通信。

**初始化**:
```python
from jumpserver_api.jms_api_client import JumpServerClient
from jumpserver_api.jms_ssh_guide import SSHGuideConnector

client = JumpServerClient(config)
connector = SSHGuideConnector(client)
```

**核心方法**:

- **`get_connection_token(asset, account, protocol="ssh", input_username="", input_secret="", connect_method="ssh_guide", connect_options=None)`**
  
  获取 SSH 向导连接令牌。
  
  参数说明：
  - `asset` (str): 资产 UUID，例如 `"2fcc289b-f985-4e51-bde9-65d63bf47cca"`
  - `account` (str): 账号 UUID，例如 `"fb13bca0-6136-4d83-9bc0-6de7087d99fd"`
  - `protocol` (str): 协议类型，默认 `"ssh"`
    - 支持的协议: `ssh`, `rdp`, `telnet`, `vnc`, `mysql`, `mariadb`, `mongodb`, `postgresql`
  - `input_username` (str): 输入的用户名（可选）
  - `input_secret` (str): 输入的密码/密钥（可选）
  - `connect_method` (str): 连接方法，默认 `"ssh_guide"`
  - `connect_options` (Dict): 连接选项字典
  
  返回值：
  - `Dict[str, Any]`: 包含 `id` 和 `value` 的连接令牌字典
  
  异常：
  - `SSHConnectionTokenError`: 当获取令牌失败时抛出

- **`get_connection_credentials(asset, account, protocol="ssh", ...)`**
  
  便利方法，直接返回连接凭证对 (用户名, 密码)。
  
  返回值：
  - `tuple[str, str]`: (用户名, 密码) 元组

### 2. CLI Tools: `jms_ssh_guide_cli.py`

命令行工具，提供易用的命令行接口。

## 使用指南

### 前置条件

1. 配置好 JumpServer API 连接信息
2. 拥有对目标资产和账号的访问权限
3. 资产和账号可以通过名称、地址、用户名或 UUID 标识

### 通过 Python 代码使用

#### 最简单的方式（推荐）- 使用资产和账号名称

```python
from jumpserver_api.jms_runtime import create_client
from jumpserver_api.jms_ssh_guide import SSHGuideConnector

# 创建客户端
client = create_client()

# 创建连接器
connector = SSHGuideConnector(client)

# 使用资产名称和账号用户名获取连接令牌
# 无需 UUID，自动自动查询和解析！
token = connector.get_connection_token(
    asset="server-prod-01",        # 资产名称（而不是 UUID）
    account="root",                # 账号用户名（而不是 UUID）
    protocol="ssh"
)

# 使用令牌连接
username = token['id']
password = token['value']
print(f"SSH连接命令: ssh {username}@target_host")
```

#### 便捷方法 - 直接获取凭证对

```python
from jumpserver_api.jms_runtime import create_client
from jumpserver_api.jms_ssh_guide import SSHGuideConnector

client = create_client()
connector = SSHGuideConnector(client)

# 直接获取用户名和密码
username, password = connector.get_connection_credentials(
    asset="server-prod-01",
    account="root"
)

print(f"Username: {username}")
print(f"Password: {password}")
```

#### 完整高级用法 - 指定所有选项

```python
token = connector.get_connection_token(
    asset="server-prod-01",
    account="root",
    protocol="ssh",
    input_username="",
    input_secret="",
    connect_method="ssh_guide",
    connect_options={
        "charset": "utf-8",
        "token_reusable": False,
        "resolution": "1920x1080"
    },
    auto_resolve=True  # 自动查询资产和账号
)
```

### 通过命令行使用

#### 使用资产和账号名称（最新版）

**获取完整令牌信息：**
```bash
cd /path/to/skills
python3 scripts/jumpserver_api/jms_ssh_guide_cli.py get-token \
  --asset server-prod-01 \
  --account root \
  --protocol ssh \
  --output json
```

**获取连接凭证（仅用户名和密码）：**
```bash
python3 scripts/jumpserver_api/jms_ssh_guide_cli.py get-credentials \
  --asset server-prod-01 \
  --account root
```

#### 支持的资产和账号标识方式

| 类型 | 示例 | 说明 |
|------|------|------|
| **资产** | | |
| UUID | `2fcc289b-f985-4e51-bde9-65d63bf47cca` | 完整的资产 UUID |
| 名称 | `server-prod-01` | 资产的友好名称 |
| IP 地址 | `192.168.1.100` | 资产的 IP 地址 |
| 混合格式 | `server-prod-01(192.168.1.100)` | 名称和地址的组合 |
| **账号** | | |
| UUID | `fb13bca0-6136-4d83-9bc0-6de7087d99fd` | 完整的账号 UUID |
| 用户名 | `root` | 账号的用户名 |
| 账号名称 | `root_account` | 账号的友好名称 |
| 混合格式 | `root_account(root)` | 名称和用户名的组合 |

#### 高级选项

```bash
python3 scripts/jumpserver_api/jms_ssh_guide_cli.py get-token \
  --asset server-prod-01 \
  --account root \
  --protocol ssh \
  --connect-method ssh_guide \
  --charset utf-8 \
  --token-reusable false \
  --resolution auto \
  --output json
```

输出格式选项 `--output`：
- `json` (默认): JSON 格式输出
- `table`: 表格格式输出
- `raw`: 原始格式输出

### 通过代码使用（原始 UUID 方式）

```python
from jumpserver_api.jms_api_client import JumpServerClient
from jumpserver_api.jms_ssh_guide import SSHGuideConnector
from jumpserver_api.jms_types import JumpServerConfig

config = JumpServerConfig(
    base_url="http://10.1.12.62",
    access_key="your_access_key",
    secret_key="your_secret_key"
)
client = JumpServerClient(config)

# 创建连接器
connector = SSHGuideConnector(client)

# 使用 UUID 获取令牌（不自动解析）
token = connector.get_connection_token(
    asset="2fcc289b-f985-4e51-bde9-65d63bf47cca",
    account="fb13bca0-6136-4d83-9bc0-6de7087d99fd",
    protocol="ssh",
    auto_resolve=False  # 禁用自动解析，直接使用 UUID
)

# 使用令牌连接
username = token['id']
password = token['value']
```

## 自动解析功能说明 (Auto-Resolve)

默认情况下，SSH 向导连接器会自动解析资产和账号标识：

### 工作流程

1. **输入识别**: 接收用户输入的资产/账号标识
2. **UUID 检查**: 如果输入是 UUID 格式，直接使用
3. **列表查询**: 查询当前组织的所有资产和账号
4. **名称匹配**: 进行精确和模糊匹配
5. **歧义检测**: 如果匹配到多个结果，给出明确错误提示
6. **UUID 返回**: 返回唯一匹配项的 UUID

### 匹配规则

#### 资产匹配（按优先级）

1. **精确 UUID 匹配**: 输入的 UUID 完全相同
2. **精确名称匹配**: 输入与资产名称完全相同（不区分大小写）
3. **精确地址匹配**: 输入与资产 IP 地址完全相同
4. **模糊名称匹配**: 输入包含在资产名称中
5. **模糊地址匹配**: 输入包含在资产地址中

#### 账号匹配（按优先级）

1. **精确 UUID 匹配**: 输入的 UUID 完全相同
2. **精确用户名匹配**: 输入与账号用户名完全相同（不区分大小写）
3. **精确名称匹配**: 输入与账号名称完全相同（不区分大小写）
4. **模糊用户名匹配**: 输入包含在账号用户名中
5. **模糊名称匹配**: 输入包含在账号名称中

### 禁用自动解析

如果需要直接使用 UUID（跳过查询），设置 `auto_resolve=False`：

```python
# Python API
token = connector.get_connection_token(
    asset="2fcc289b-f985-4e51-bde9-65d63bf47cca",
    account="fb13bca0-6136-4d83-9bc0-6de7087d99fd",
    auto_resolve=False  # 禁用自动解析
)
```

```bash
# CLI 目前不支持禁用自动解析，总是自动解析


## 连接选项 (Connect Options) 详解

`connect_options` 字典控制连接的行为，包含以下常用字段：

| 选项 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| `charset` | string | `"default"` | 字符集编码 |
| `disableautohash` | boolean | `false` | 是否禁用自动 hash 验证 |
| `token_reusable` | boolean | `false` | 获取的令牌是否可重复使用 |
| `resolution` | string | `"auto"` | 分辨率（仅 RDP 使用），如 `"1920x1080"` |
| `backspaceAsCtrlH` | boolean | `false` | Backspace 键是否作为 Ctrl+H 发送（仅终端使用） |
| `appletConnectMethod` | string | `"web"` | Applet 连接方法：`"web"` 或 `"local"` |
| `virtualappConnectMethod` | string | `"web"` | 虚拟应用连接方法：`"web"` 或 `"local"` |
| `reusable` | boolean | `false` | 连续是否可重用 |
| `rdp_connection_speed` | string | `"auto"` | RDP 连接速度，枚举值：`"auto"`, `"modem"`, `"broadband"`, `"lan"` |

## 常见操作场景

### 场景 1: 获取 SSH 连接凭证

```python
from jumpserver_api.jms_runtime import create_client
from jumpserver_api.jms_ssh_guide import SSHGuideConnector

client = create_client()
connector = SSHGuideConnector(client)

username, password = connector.get_connection_credentials(
    asset="<asset-uuid>",
    account="<account-uuid>",
    protocol="ssh"
)

# 使用凭证连接
import os
os.system(f"sshpass -p '{password}' ssh {username}@target_host")
```

### 场景 2: 获取 RDP 连接凭证

```python
connector = SSHGuideConnector(client)

token = connector.get_connection_token(
    asset="<asset-uuid>",
    account="<account-uuid>",
    protocol="rdp",
    connect_options={
        "resolution": "1920x1080",
        "rdp_connection_speed": "lan"
    }
)

# 使用 RDP 连接
rdp_username = token['id']
rdp_password = token['value']
```

### 场景 3: 获取数据库连接凭证

```python
connector = SSHGuideConnector(client)

token = connector.get_connection_token(
    asset="<asset-uuid>",
    account="<account-uuid>",
    protocol="mysql",  # 或 'mariadb', 'postgresql', 'mongodb'
)

db_username = token['id']
db_password = token['value']
```

## 错误处理

```python
from jumpserver_api.jms_ssh_guide import SSHConnectionTokenError

try:
    token = connector.get_connection_token(
        asset="invalid-uuid",
        account="invalid-uuid"
    )
except SSHConnectionTokenError as e:
    print(f"获取令牌失败: {e}")
    print(f"错误详情: {e.details}")
```

## 常见错误及解决

| 错误 | 原因 | 解决方案 |
|-----|------|--------|
| 404 Not Found | API 端点不可用或 JumpServer 版本不支持 | 检查 JumpServer 版本是否 >= v4.10 |
| 401 Unauthorized | 认证失败 | 检查 API 凭证（access_key, secret_key）是否正确 |
| 403 Forbidden | 无访问权限 | 检查用户是否有该资产和账号的访问权限 |
| 400 Bad Request | 请求参数错误 | 检查 asset、account 是否有效，protocol 是否支持 |
| Connection Token Error | 令牌获取失败 | 检查响应是否包含 `id` 和 `value` 字段 |

## 集成示例

### 与 JumpServer 查询模块集成

```python
from jumpserver_api.jms_query import (
    # 假设存在这些查询函数
    get_user_accessible_assets,
    get_asset_accounts
)
from jumpserver_api.jms_ssh_guide import SSHGuideConnector

# 1. 查询用户可访问的资产
assets = get_user_accessible_assets(client, username="example.user")

# 2. 获取资产下的账号
accounts = get_asset_accounts(client, asset_id=assets[0]['id'])

# 3. 获取连接令牌
connector = SSHGuideConnector(client)
token = connector.get_connection_token(
    asset=assets[0]['id'],
    account=accounts[0]['id']
)

print(f"Username: {token['id']}, Password: {token['value']}")
```

## API 兼容性

该功能需要 JumpServer API v1 支持，具体版本要求：
- **JumpServer >= v4.10**: 完全支持所有功能
- **JumpServer < v4.10**: 不支持此 API 端点

## 性能和安全考虑

1. **令牌有效期**: 通常来说，连接令牌有一定的时间有效期，不应长时间保存
2. **重用策略**: 设置 `token_reusable=false` 获取一次性令牌（更安全）
3. **日志**: 避免在日志中记录返回的密码/令牌
4. **TLS 验证**: 生产环境建议启用 TLS 验证

```python
config = JumpServerConfig(
    base_url="https://jumpserver.example.com",
    # ...
    verify_tls=True  # 启用 TLS 验证
)
```

## 文件结构

```
scripts/jumpserver_api/
├── jms_ssh_guide.py          # 核心模块
├── jms_ssh_guide_cli.py      # CLI 工具（仅用于调试/开发）
└── ...
```

## 相关文档

- [JumpServer API 文档](http://10.1.12.62/docs/api/)
- [堡垒机 SSH 连接流程](../references/routing-playbook.md)
- [权限管理](../references/permissions.md)

## 常见问题 (FAQ)

**Q: 资产和账号 UUID 是什么？如何获取？**

A: UUID 是资产和账号的唯一标识符。**但现在您无需手动查找 UUID**！直接使用资产名称或账号用户名：

```bash
# 新方式 - 无需 UUID（自动解析）
python3 scripts/jumpserver_api/jms_ssh_guide_cli.py get-credentials \
  --asset server-prod-01 \
  --account root

# 旧方式 - 使用 UUID（如果需要）
python3 scripts/jumpserver_api/jms_ssh_guide_cli.py get-credentials \
  --asset 2fcc289b-f985-4e51-bde9-65d63bf47cca \
  --account fb13bca0-6136-4d83-9bc0-6de7087d99fd
```

如果需要查看 UUID，可以运行：
```bash
python3 scripts/jumpserver_api/jms_diagnose.py user-assets --username <username>
```

**Q: 如何指定资产和账号，如果我不知道它们的确切名称？**

A: 系统会自动进行模糊匹配。例如：
- 输入 `prod` 会匹配 `server-prod-01`
- 输入 `192.168.1` 会匹配 `192.168.1.100`
- 输入 `ro` 会匹配 `root` 用户名

如果匹配到多个结果，系统会列出候选项，您可以使用更精确的名称重试。

**Q: 如何查看当前可用的所有资产和账号？**

A: 使用诊断命令查看用户可访问的资产和账号：

```bash
# 查看当前用户可访问的资产
python3 scripts/jumpserver_api/jms_diagnose.py user-assets --org-name Default

# 查看某个资产下的所有账号
python3 scripts/jumpserver_api/jms_query.py assets --name server-prod-01 --filter
```

**Q: 如何获取 SSH 连接句凭证后立即连接？**

A: 使用便捷方法 `get-credentials` 获取用户名和密码，然后使用 `sshpass` 或密钥连接：

```bash
# 方法 1: 使用 sshpass（密码连接）
python3 scripts/jumpserver_api/jms_ssh_guide_cli.py get-credentials \
  --asset server-prod-01 \
  --account root \
  --output json | jq -r '.username + ":" + .password' > creds.tmp

creds=$(cat creds.tmp)
username="${creds%%:*}"
password="${creds##*:}"
sshpass -p "$password" ssh "$username@target_host"

# 方法 2: 使用 SSH 密钥（更安全）
# 如果堡垒机返回的密钥可用，保存为文件后使用：
ssh -i <key_file> "$username@target_host"
```

**Q: 令牌被获取后是否可以多次使用？**

A: 默认情况下，令牌是一次性的（`token_reusable=false`）。如需可重用令牌，设置：

```python
token = connector.get_connection_token(
    asset="server-prod-01",
    account="root",
    connect_options={"token_reusable": True}
)
```

```bash
# CLI 目前不支持此选项，建议使用 Python API
```

**Q: 如何处理连接失败或识别出错？**

A: 系统会给出详细的错误提示。常见情况：

1. **资产找不到**: 检查资产名称是否正确，或使用 UUID
2. **资产模糊匹配**: 使用更精确的名称或 IP 地址
3. **账号找不到**: 检查用户名是否正确
4. **权限不足**: 检查用户是否有该资产的访问权限

**Q: 如何调试解析问题？**

A: 启用 Python 代码的详细输出：

```python
from jumpserver_api.jms_ssh_guide import SSHGuideConnector

connector = SSHGuideConnector(client)

# 分步测试解析过程
try:
    asset_id = connector.resolve_asset_id("server-prod-01")
    print(f"✓ 资产 ID: {asset_id}")
except Exception as e:
    print(f"✗ 资产解析失败: {e}")

try:
    account_id = connector.resolve_account_id("root", asset_id=asset_id)
    print(f"✓ 账号 ID: {account_id}")
except Exception as e:
    print(f"✗ 账号解析失败: {e}")
```

**Q: 如何集成到现有的自动化脚本中？**

A: 推荐通过 Python 代码集成（最灵活）或 CLI + 脚本（最简单）：

```bash
#!/bin/bash
# 获取连接凭证
creds_json=$(python3 scripts/jumpserver_api/jms_ssh_guide_cli.py get-credentials \
  --asset "$ASSET_NAME" \
  --account "$ACCOUNT_NAME" \
  --output json)

# 解析 JSON
username=$(echo "$creds_json" | jq -r '.username')
password=$(echo "$creds_json" | jq -r '.password')

# 使用凭证连接或其他操作
echo "Username: $username"
echo "Password: $password"
```

**Q: 旧的 UUID 方式还能用吗？**

A: 完全可以！系统兼容 UUID 和名称。您可以继续使用 UUID，或切换到更方便的名称方式：

```python
# 两种方式都支持
connector.get_connection_token(asset="server-prod-01", account="root")  # 新方式：名称
connector.get_connection_token(asset="2fcc...", account="fb13...")  # 旧方式：UUID
```

**Q: 如果有多个资产或账号名称相似怎么办？**

A: 系统会检测到歧义并给出明确的错误提示，列出所有匹配的候选项。使用更精确的标识符：

```bash
# 如果 "server" 匹配到多个资产，使用更精确的名称
python3 scripts/jumpserver_api/jms_ssh_guide_cli.py get-credentials \
  --asset "server-prod-01" \
  --account root
```

**Q: 支持的资产名称格式有哪些？**

A: 支持任何资产的 `name` 或 `address` 字段值：
- 资产名称: `server-prod-01`
- IP 地址: `192.168.1.100`
- 域名: `prod.example.com`
- 混合格式（自动分解）: `server-prod-01(192.168.1.100)`

## 代码示例汇总

### 最简单的使用方式

```python
from jumpserver_api.jms_runtime import create_client
from jumpserver_api.jms_ssh_guide import SSHGuideConnector

client = create_client()
connector = SSHGuideConnector(client)

# 最简单！直接用资产名称和账号用户名，自动查询解析
username, password = connector.get_connection_credentials(
    asset="server-prod-01",      # 资产名称，自动查询 UUID
    account="root"               # 账号用户名，自动查询 UUID
)

print(f"Username: {username}")
print(f"Password: {password}")
```

### 如果需要完整令牌信息

```python
token = connector.get_connection_token(
    asset="server-prod-01",
    account="root",
    protocol="ssh"
)

print(f"Full token: {token}")
```

### 禁用自动解析（直接使用 UUID）

```python
# 如果已知 UUID，可以禁用自动解析以提高速度
token = connector.get_connection_token(
    asset="2fcc289b-f985-4e51-bde9-65d63bf47cca",
    account="fb13bca0-6136-4d83-9bc0-6de7087d99fd",
    auto_resolve=False
)
```

### 与其他工具集成

```python
from jumpserver_api.jms_runtime import create_client
from jumpserver_api.jms_ssh_guide import SSHGuideConnector
from jumpserver_api.jms_diagnose import user_assets

# 1. 先查询用户可访问的资产
client = create_client()
assets = user_assets(client, username="example.user", discovery=None)

# 2. 从结果中选择一个资产
asset_name = assets[0]['name']

# 3. 获取该资产下的账号列表并连接
connector = SSHGuideConnector(client)
username, password = connector.get_connection_credentials(
    asset=asset_name,
    account="root"
)

print(f"连接信息: {username}:{password}")
```

### 处理错误

```python
from jumpserver_api.jms_ssh_guide import SSHConnectionTokenError

try:
    token = connector.get_connection_token(
        asset="nonexistent-asset",
        account="root"
    )
except SSHConnectionTokenError as e:
    print(f"错误: {e}")
    print(f"详情: {e.details}")
```

更多详见项目主 README 和其他 skill 文档。
