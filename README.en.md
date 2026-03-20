# jumpserver-skills

`jumpserver-skills` is a JumpServer V4 query-oriented skill repository. It now supports environment initialization writes, including generating `.env.local` from user-provided config and persisting `JMS_ORG_ID`, while business-object and permission operations remain read-only.

## Overview

| Entry point | Purpose | Current scope |
|---|---|---|
| `scripts/jms_assets.py` | assets, accounts, users, groups, platforms, nodes, organizations | `list`, `get` |
| `scripts/jms_permissions.py` | permission rule queries | `list`, `get` |
| `scripts/jms_audit.py` | login, operate, session, command audits | `list`, `get` |
| `scripts/jms_diagnose.py` | config checks, config writes, connectivity, org selection, resolution, access analysis | env init + read-only diagnostics |

## Rules

- start with `python3 scripts/jms_diagnose.py config-status --json`
- if config is incomplete, collect user-provided env info and run `config-write --confirm`
- then run `ping`
- if org context is missing, run `select-org --org-id <org-id> --confirm`
- only the exact accessible-org sets `{0002}` or `{0002,0004}` may auto-write `0002`
- business `create/update/delete/append/remove/unblock` operations remain unsupported

## Quick Start

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Initialize config:

```bash
python3 scripts/jms_diagnose.py config-status --json
python3 scripts/jms_diagnose.py config-write --payload '{"JMS_API_URL":"https://jump.example.com","JMS_ACCESS_KEY_ID":"<ak>","JMS_ACCESS_KEY_SECRET":"<sk>","JMS_VERSION":"4"}' --confirm
python3 scripts/jms_diagnose.py ping
```

Inspect and persist org selection:

```bash
python3 scripts/jms_diagnose.py select-org
python3 scripts/jms_diagnose.py select-org --org-id <org-id>
python3 scripts/jms_diagnose.py select-org --org-id <org-id> --confirm
```

Then run queries:

```bash
python3 scripts/jms_assets.py list --resource user --filters '{"username":"demo-user"}'
python3 scripts/jms_permissions.py list --filters '{"limit":20}'
python3 scripts/jms_audit.py list --audit-type operate --filters '{"limit":30}'
```

## Environment Model

| Variable | Notes |
|---|---|
| `JMS_API_URL` or `JMS_WEB_URL` | JumpServer address |
| `JMS_ACCESS_KEY_ID` + `JMS_ACCESS_KEY_SECRET` | AK/SK auth |
| `JMS_USERNAME` + `JMS_PASSWORD` | basic auth |
| `JMS_ORG_ID` | current query org |
| `JMS_VERSION` | defaults to `4` |
| `JMS_TIMEOUT` | optional |

Notes:

- `config-write --confirm` can generate or update `.env.local`
- `select-org --confirm` can persist `JMS_ORG_ID`
- business entry points still stay read-only

## Unsupported Scope

- asset, platform, node, account, user, user-group, and organization mutations
- permission create/update/append/remove/delete
- temporary SDK/HTTP scripts that bypass the supported workflow
