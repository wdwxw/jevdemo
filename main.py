"""用一个请求测试 TypeSafe System One API 的三种结构化判断能力。"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient


# 无论从哪个工作目录启动，都只读取脚本同目录的 .env。
ENV_FILE = Path(__file__).with_name(".env")
load_dotenv(ENV_FILE)


DEFAULT_STATE = (
    "Hi, I've been trying to connect my Stripe account for 3 days and the "
    "integration keeps failing. I'm losing sales. Please help ASAP."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="测试 TypeSafe Jev 的 Choice、Score 和 Noul 能力。"
    )
    parser.add_argument(
        "state",
        nargs="?",
        default=DEFAULT_STATE,
        help="要评估的文本；不传时使用内置客服工单示例。",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("TYPESAFE_DEFAULT_MODEL", "jev-latest"),
        help="模型名，默认读取 TYPESAFE_DEFAULT_MODEL，否则使用 jev-latest。",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="只列出当前账号可用的模型，不执行评估。",
    )
    return parser.parse_args()


def require_api_key() -> None:
    if not os.getenv("TYPESAFE_API_KEY", "").strip():
        raise SystemExit(
            f"缺少 TYPESAFE_API_KEY。请确认文件存在：{ENV_FILE}\n"
            "注意：应编辑 .env，而不是 .env.example；变量名不能带反斜杠。"
        )


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, default=str))


def list_models(client: TypeSafeClient) -> None:
    models = client.models.list()
    print_json(
        [
            {
                "name": model.name,
                "release_date": model.release_date,
                "description": model.description,
            }
            for model in models.models
        ]
    )


def evaluate_api(client: TypeSafeClient, state: str) -> dict[str, Any]:
    result = client.system_one(
        state=state,
        questions={
            "department": Choice(
                instructions="Which team should handle this request?",
                criteria={
                    "billing": "Payments, subscriptions, invoices, or refunds",
                    "technical": "Bugs, outages, or integration problems",
                    "sales": "Pricing, upgrades, or new-account questions",
                },
            ),
            "frustration": Score(
                instructions="How frustrated does the customer appear?",
                criteria=[
                    "Calm and only stating facts",
                    "Frustrated but civil",
                    "Very angry or using strong language",
                ],
            ),
            "is_urgent": Noul(
                instructions="Does the message convey urgency or time-sensitivity?",
                criteria={
                    "true": "The customer explicitly signals urgency or active loss",
                    "false": "No urgency or time pressure is expressed",
                },
            ),
        },
    )

    # 使用原始 JSON 让 CLI 和网页都能看到完整的概率、置信度与 token 用量。
    return result.raw_http_response.json()


def main() -> int:
    args = parse_args()
    require_api_key()

    try:
        with TypeSafeClient(model=args.model) as client:
            if args.list_models:
                list_models(client)
            else:
                print_json(evaluate_api(client, args.state))
    except Exception as error:
        print(f"TypeSafe API 调用失败：{error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
