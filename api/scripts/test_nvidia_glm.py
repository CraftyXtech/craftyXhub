#!/usr/bin/env python3
"""
Smoke-test a configured chat model through its active provider route.

Run from the api directory:
    venv/bin/python scripts/test_nvidia_glm.py --model deepseek-v4-pro
"""

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pydantic_ai import Agent

from core.config import settings
from services.ai.llm_config import get_blog_model_capabilities, get_model


async def main() -> int:
    parser = argparse.ArgumentParser(description="Test configured blog model routing")
    parser.add_argument("--model", default="deepseek-v4-pro")
    parser.add_argument(
        "--prompt",
        default="Reply with one sentence confirming the model is reachable through its configured provider.",
    )
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()

    capabilities = get_blog_model_capabilities(args.model)
    provider_type = capabilities.get("provider_type")
    if provider_type == "nvidia" and not settings.NVIDIA_API_KEY:
        print("NVIDIA_API_KEY is not configured.", flush=True)
        return 2
    if provider_type == "deepseek" and not settings.DEEPSEEK_API_KEY:
        print("DEEPSEEK_API_KEY is not configured.", flush=True)
        return 2
    if provider_type == "openrouter" and not settings.OPENROUTER_API_KEY:
        print("OPENROUTER_API_KEY is not configured.", flush=True)
        return 2

    print("provider_type:", capabilities.get("provider_type"), flush=True)
    print("extra_body:", capabilities.get("extra_body"), flush=True)

    agent = Agent(
        get_model(args.model),
        output_type=str,
        system_prompt="You are a concise API smoke-test assistant.",
    )
    result = await asyncio.wait_for(
        agent.run(
            args.prompt,
            model_settings={
                "max_tokens": 120,
                "temperature": 0.2,
                "extra_body": capabilities.get("extra_body") or {},
                "timeout": args.timeout,
            },
        ),
        timeout=args.timeout + 5,
    )
    print(str(getattr(result, "output", getattr(result, "data", ""))).strip(), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
