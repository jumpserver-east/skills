# 新增能力说明

本文档说明近期新增的两个 capability：组件负载概览与改密失败报错分析报表。

## 1) 组件负载概览

- capability_id: `component-load-overview`
- 入口: `python3 scripts/jumpserver_api/jms_diagnose.py inspect --capability component-load-overview --days 1`
- 主要来源接口: `/api/v1/terminal/terminals/`

### 适用问题

- 查询 JumpServer 各组件负载
- 查询组件 CPU、内存、磁盘、在线会话
- 查询组件是否高负载或存活状态

### 输出重点

- `summary.component_count`: 组件总数
- `summary.metric_ready_count`: 有负载指标的组件数
- `summary.high_load_component_count`: 高负载组件数
- `records[]`:
  - `component_name`, `component_type`, `remote_addr`
  - `is_alive`, `is_active`
  - `cpu_usage_percent`, `memory_usage_percent`, `disk_usage_percent`
  - `session_count`, `load_value`, `load_label`
  - `is_high_load`

### 高负载判定阈值

- CPU `>= 80`
- 内存 `>= 80`
- 磁盘 `>= 85`
- 或 `load_value >= 0.8`

满足任一条件即判定 `is_high_load=true`。

## 2) 改密失败报错分析报表

- capability_id: `change-password-failure-report`
- 入口: `python3 scripts/jumpserver_api/jms_diagnose.py inspect --capability change-password-failure-report --days 30`
- 主要来源接口: `/api/v1/audits/password-change-logs/`

### 适用问题

- 改密失败日志分析
- 统计报错类型、报错资产
- 统计成功/失败数量与占比

### 输出重点

- `summary.total`: 改密总数
- `summary.success_total`, `summary.failed_total`
- `summary.success_rate`, `summary.failure_rate`
- `summary.top_error_types`: 失败报错类型 Top
- `summary.top_failed_assets`: 失败资产 Top
- `summary.top_failed_users`: 失败用户 Top
- `records[]`: 失败明细（`user`, `asset`, `account`, `change_by`, `remote_addr`, `error_type`, `timestamp`）

### 失败识别口径

- 先读状态与错误字段（如 `status/reason/detail/message/error/type`）
- 命中失败关键词（如 `fail/failed/error/denied/失败/错误/超时`）即判为失败
- 未命中的错误类别归类为 `unknown`
