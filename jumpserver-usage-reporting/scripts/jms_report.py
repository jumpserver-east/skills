#!/usr/bin/env python3
from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
JUMPSERVER_API_ROOT = REPO_ROOT / "jumpserver-api"
LOCAL_ENTRYPOINT = "jumpserver-usage-reporting/scripts/jms_report.py"


if __name__ == "__main__":
    if not JUMPSERVER_API_ROOT.exists():
        raise SystemExit(
            "Missing jumpserver-api directory: %s. Register this subskill from the full repository checkout."
            % JUMPSERVER_API_ROOT
        )
    sys.path.insert(0, str(JUMPSERVER_API_ROOT))

    report_module = import_module("jms_report")
    runtime_module = import_module("jms_runtime")

    runtime_module.set_entrypoint_override("jms_report.py", LOCAL_ENTRYPOINT)
    raise SystemExit(report_module.main())
