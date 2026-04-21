# 单 skill 注册说明

这份文档说明如何在“宿主一次只能注册一个 skill”的情况下使用当前仓库。

## 适用前提

- 宿主只能选择一个 skill 根目录
- 你希望直接注册某个子 skill，而不是根目录总路由 skill
- 当前机器上保留的是完整仓库，而不是只复制了某个子目录

## 推荐注册方式

按需选择一个子 skill 目录作为 skill 根目录，并使用该目录下的 `agents/openai.yaml`：

| 子 skill 目录 | 接入描述 | 本地入口 |
|---|---|---|
| `jumpserver-runtime-setup/` | `jumpserver-runtime-setup/agents/openai.yaml` | `jumpserver-runtime-setup/scripts/jms_diagnose.py` |
| `jumpserver-object-query/` | `jumpserver-object-query/agents/openai.yaml` | `jumpserver-object-query/scripts/jms_query.py` |
| `jumpserver-effective-access/` | `jumpserver-effective-access/agents/openai.yaml` | `jumpserver-effective-access/scripts/jms_diagnose.py` |
| `jumpserver-permission-analysis/` | `jumpserver-permission-analysis/agents/openai.yaml` | `jumpserver-permission-analysis/scripts/jms_query.py`、`jumpserver-permission-analysis/scripts/jms_diagnose.py` |
| `jumpserver-audit-investigation/` | `jumpserver-audit-investigation/agents/openai.yaml` | `jumpserver-audit-investigation/scripts/jms_query.py`、`jumpserver-audit-investigation/scripts/jms_diagnose.py` |
| `jumpserver-usage-reporting/` | `jumpserver-usage-reporting/agents/openai.yaml` | `jumpserver-usage-reporting/scripts/jms_report.py` |
| `jumpserver-governance-inspection/` | `jumpserver-governance-inspection/agents/openai.yaml` | `jumpserver-governance-inspection/scripts/jms_diagnose.py` |

## 本地入口机制

- 每个子 skill 的本地 `scripts/*.py` 都是真实入口脚本
- 本地入口会从仓库根目录加载共享底层 `jumpserver-api/*.py`
- 这样做的目的是让“子 skill 目录本身就是 skill 根目录”时，命令路径仍然稳定，同时不再让某个子 skill 目录充当全部 Python 代码的宿主

例子：

- 在 `jumpserver-object-query/` 目录作为 skill 根目录时，用 `python3 scripts/jms_query.py object-list ...`
- 本地入口会从仓库里的共享实现 `jumpserver-api/jms_query.py` 加载对象查询 profile

## 重要限制

- 当前方案要求完整仓库目录仍然存在，因为 wrapper、共享 `references/` 和 `template/` 都依赖仓库相邻路径
- 如果宿主只能上传一个完全自包含的独立目录，而不能保留仓库其他目录，这套轻量包装还不够
- 这种“完全自包含”的导出模式会复制共享运行时、references 和模板，目前仓库里还没有自动打包脚本

## 什么时候仍然用根目录 skill

优先用根目录 [SKILL.md](../SKILL.md) 的情况：

- 宿主支持多 skill 或至少允许根目录总路由存在
- 你希望先让模型自己判断是对象查询、权限分析、审计调查还是报告
- 你不想预先为宿主选定一个窄领域子 skill

## 建议

- 想要最稳妥的单 skill 接入：直接注册对应子目录，并使用它自己的 `agents/openai.yaml`
- 想要最高兼容性：继续注册仓库根目录的总路由 skill
- 想要完全自包含的发布包：后续再补一个导出脚本，把共享 runtime 和 references vendor 到单独产物目录