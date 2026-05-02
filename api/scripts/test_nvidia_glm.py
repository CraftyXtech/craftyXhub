#!/usr/bin/env python3
"""
Smoke-test GLM 5.1 through the configured NVIDIA NIM route.

Run from the api directory:
    venv/bin/python scripts/test_nvidia_glm.py
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
    parser = argparse.ArgumentParser(description="Test NVIDIA GLM 5.1 routing")
    parser.add_argument(
        "--prompt",
        default="Reply with one sentence confirming GLM 5.1 is reachable through NVIDIA.",
    )
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()

    if not settings.NVIDIA_API_KEY:
        print("NVIDIA_API_KEY is not configured.", flush=True)
        return 2

    capabilities = get_blog_model_capabilities("glm-5.1")
    print("provider_type:", capabilities.get("provider_type"), flush=True)
    print("extra_body:", capabilities.get("extra_body"), flush=True)

    agent = Agent(
        get_model("glm-5.1"),
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
