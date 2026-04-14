#!/usr/bin/env python3
"""
堡垒机 SSH 向导连接 CLI - jms_ssh_guide.py

该脚本提供命令行接口用于获取堡垒机 SSH 向导连接的临时令牌。

使用示例：
  python3 scripts/jumpserver_api/jms_ssh_guide.py \\
    --asset 2fcc289b-f985-4e51-bde9-65d63bf47cca \\
    --account fb13bca0-6136-4d83-9bc0-6de7087d99fd \\
    --protocol ssh

  python3 scripts/jumpserver_api/jms_ssh_guide.py get-token \\
    --asset <asset-uuid> \\
    --account <account-uuid> \\
    --protocol ssh \\
    --output json

配置说明：
  - 需要配置有效的 JumpServer API 连接信息
  - 默认从环境变量或 .env 文件读取配置
  - 资产和账号必须存在且用户有访问权限
"""

from __future__ import annotations

if __package__ in {None, ""}:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jumpserver_api.jms_bootstrap import ensure_requirements_installed

ensure_requirements_installed()

import argparse
import json
import sys
from typing import Any, Dict, Optional

from jumpserver_api.jms_runtime import (
    CLIError,
    CLIHelpFormatter,
    create_client,
    ensure_selected_org_context,
)
from jumpserver_api.jms_ssh_guide import SSHGuideConnector, SSHConnectionTokenError


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="堡垒机 SSH 向导连接令牌获取工具",
        formatter_class=CLIHelpFormatter,
    )

    # 全局选项
    parser.add_argument(
        "--config-file",
        type=str,
        default=None,
        help="JumpServer 配置文件路径（默认：~/.jumpserver/config.json）",
    )
    parser.add_argument(
        "--verify-tls",
        type=bool,
        default=None,
        help="是否验证 TLS 证书（默认：False）",
    )
    parser.add_argument(
        "--output",
        choices=["json", "table", "raw"],
        default="json",
        help="输出格式（默认：json）",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="命令",
    )

    # get-token 子命令
    get_token_parser = subparsers.add_parser(
        "get-token",
        help="获取 SSH 向导连接令牌",
        formatter_class=CLIHelpFormatter,
    )
    get_token_parser.add_argument(
        "--asset",
        type=str,
        required=True,
        help="资产标识（必需），可以是 UUID、资产名称或 IP 地址。示例：server-prod-01 或 192.168.1.100",
    )
    get_token_parser.add_argument(
        "--account",
        type=str,
        required=True,
        help="账号标识（必需），可以是 UUID、账号名称或用户名。示例：root 或 root_account",
    )
    get_token_parser.add_argument(
        "--protocol",
        type=str,
        default="ssh",
        help="协议类型，默认 ssh（支持：ssh, rdp, telnet, vnc, mysql, mariadb, mongodb, postgresql）",
    )
    get_token_parser.add_argument(
        "--username",
        type=str,
        default="",
        help="输入的用户名（可选，默认使用账号的用户名）",
    )
    get_token_parser.add_argument(
        "--secret",
        type=str,
        default="",
        help="输入的密码/密钥（可选，默认使用账号的密码）",
    )
    get_token_parser.add_argument(
        "--connect-method",
        type=str,
        default="ssh_guide",
        help="连接方法（默认：ssh_guide）",
    )
    get_token_parser.add_argument(
        "--charset",
        type=str,
        default="default",
        help="字符集（默认：default）",
    )
    get_token_parser.add_argument(
        "--token-reusable",
        type=bool,
        default=False,
        help="令牌是否可重用（默认：False）",
    )
    get_token_parser.add_argument(
        "--resolution",
        type=str,
        default="auto",
        help="分辨率设置（默认：auto）",
    )

    # get-credentials 子命令（便利命令）
    get_creds_parser = subparsers.add_parser(
        "get-credentials",
        help="获取连接凭证（仅返回用户名和密码）",
        formatter_class=CLIHelpFormatter,
    )
    get_creds_parser.add_argument(
        "--asset",
        type=str,
        required=True,
        help="资产标识（必需），可以是 UUID、资产名称或 IP 地址",
    )
    get_creds_parser.add_argument(
        "--account",
        type=str,
        required=True,
        help="账号标识（必需），可以是 UUID、账号名称或用户名",
    )
    get_creds_parser.add_argument(
        "--protocol",
        type=str,
        default="ssh",
        help="协议类型，默认 ssh",
    )

    return parser


def format_output(data: Any, format_type: str) -> str:
    """格式化输出"""
    if format_type == "json":
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)
    elif format_type == "table":
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                lines.append(f"{key:20} : {value}")
            return "\n".join(lines)
        return str(data)
    else:  # raw
        return str(data)


def cmd_get_token(args: argparse.Namespace) -> None:
    """执行 get-token 命令"""
    try:
        client = create_client()
        ensure_selected_org_context(client)
    except CLIError as exc:
        print(f"错误：{exc.message}", file=sys.stderr)
        sys.exit(1)

    connector = SSHGuideConnector(client)

    # 构建连接选项
    connect_options = {
        "charset": args.charset,
        "token_reusable": args.token_reusable,
        "resolution": args.resolution,
    }

    try:
        token = connector.get_connection_token(
            asset=args.asset,
            account=args.account,
            protocol=args.protocol,
            input_username=args.username,
            input_secret=args.secret,
            connect_method=args.connect_method,
            connect_options=connect_options,
        )

        result = {
            "status": "success",
            "message": "已获取连接令牌",
            "token": token,
            "connection_info": {
                "username": token.get("id"),
                "password": token.get("value"),
            },
        }

        print(format_output(result, args.output))

    except SSHConnectionTokenError as exc:
        error_result = {
            "status": "error",
            "message": str(exc),
            "error_code": "SSH_TOKEN_ERROR",
        }
        print(format_output(error_result, args.output), file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        error_result = {
            "status": "error",
            "message": f"未预期的错误：{str(exc)}",
            "error_code": "UNEXPECTED_ERROR",
        }
        print(format_output(error_result, args.output), file=sys.stderr)
        sys.exit(1)


def cmd_get_credentials(args: argparse.Namespace) -> None:
    """执行 get-credentials 命令"""
    try:
        client = create_client()
        ensure_selected_org_context(client)
    except CLIError as exc:
        print(f"错误：{exc.message}", file=sys.stderr)
        sys.exit(1)

    connector = SSHGuideConnector(client)

    try:
        username, password = connector.get_connection_credentials(
            asset=args.asset,
            account=args.account,
            protocol=args.protocol,
        )

        result = {
            "status": "success",
            "username": username,
            "password": password,
        }

        print(format_output(result, args.output))

    except SSHConnectionTokenError as exc:
        error_result = {
            "status": "error",
            "message": str(exc),
            "error_code": "SSH_TOKEN_ERROR",
        }
        print(format_output(error_result, args.output), file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        error_result = {
            "status": "error",
            "message": f"未预期的错误：{str(exc)}",
            "error_code": "UNEXPECTED_ERROR",
        }
        print(format_output(error_result, args.output), file=sys.stderr)
        sys.exit(1)


def main() -> int:
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        # 如果没有指定子命令，默认使用 get-token
        if hasattr(args, "asset") and hasattr(args, "account"):
            args.command = "get-token"
        else:
            parser.print_help()
            return 0

    if args.command == "get-token":
        cmd_get_token(args)
    elif args.command == "get-credentials":
        cmd_get_credentials(args)
    else:
        print(f"未知命令：{args.command}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
