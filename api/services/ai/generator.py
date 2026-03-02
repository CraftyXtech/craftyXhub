from pydantic_ai import Agent, RunContext
from pydantic_ai.settings import ModelSettings
from pydantic import BaseModel, Field
from core.config import settings
from .tools import ToolHandler
from .llm_config import get_model
import time
from typing import Dict, List, Any, Optional


class GenerationDeps(BaseModel):
    tool_id: str
    tone: str
    length: str
    language: str


class ContentVariant(BaseModel):
    content: str = Field(description="The generated content")
    word_count: int = Field(description="Number of words in the content")


class AIGeneratorService:
    def __init__(self):
        """
        Initialize AI service. Models are provided by the centralized
        LLM config (llm_config.py).
        """
        self.system_prompt = (
            "You are an expert content writer specializing in creating engaging, "
            "SEO-optimized content. Follow the user's instructions precisely regarding "
            "tone, length, and style. Generate high-quality, original content."
        )

    def _get_agent_for_model(self, model_name: str, system_prompt: Optional[str] = None) -> Agent:
        """
        Create an agent for the specified model.
        Delegates to the centralized LLM config (single source of truth).
        """
        system_prompt = system_prompt or self.system_prompt
        pydantic_model = get_model(model_name)

        return Agent(
            model=pydantic_model,
            output_type=str,
            system_prompt=system_prompt,
        )

    async def generate(
        self,
        tool_id: str,
        model: str,
        params: dict,
        prompt: str | None = None,
        keywords: list[str] | str | None = None,
        tone: str = "professional",
        length: str = "medium",
        language: str = "en-US",
        creativity: float = 0.7,
        variant_count: int = 1,
    ) -> Dict[str, Any]:
        start_time = time.time()
        # Try strict tool validation first; if it fails but a freeform prompt exists, we allow fallback
        try:
            ToolHandler.validate_params(tool_id, params)
            missing_ok = True
        except ValueError:
            missing_ok = False

        tool_cfg = ToolHandler.get_tool(tool_id) or {}

        built_prompt = ToolHandler.build_prompt(
            tool_id=tool_id,
            params=params,
            tone=tone,
            length=length,
            language=language,
            prompt=prompt if not missing_ok else None,
            keywords=keywords if not missing_ok else None,
        )

        # JSON mode preface when requested
        json_mode = False
        try:
            json_mode = bool(params.get("return_json")) or tool_cfg.get("output_mode") == "json"
        except Exception:
            json_mode = tool_cfg.get("output_mode") == "json"

        if json_mode:
            keys_hint = ToolHandler.get_json_keys_hint(tool_id)
            hint_text = (
                f"Return ONLY valid JSON{': with keys ' + ', '.join(keys_hint) if keys_hint else ''}. "
                "No prose, no markdown fences."
            )
            built_prompt = hint_text + "\n\n" + built_prompt

        # Get agent for the requested model
        try:
            system_prompt_override = tool_cfg.get("system_prompt") if tool_cfg else None
            agent = self._get_agent_for_model(model, system_prompt=system_prompt_override)
        except ValueError as e:
            raise ValueError(str(e))
        variants = []
        # Respect requested variant count (aligned with API schema: 1..5)
        count = max(1, min(int(variant_count or 1), 5))

        for _ in range(count):
            try:
                result = await agent.run(
                    built_prompt,
                    model_settings=ModelSettings(
                        temperature=creativity,
                        max_tokens=ToolHandler.get_max_tokens(length),
                    ),
                )

                content = result.output
                word_count = len(content.split())
                char_count = len(content)
                reading_time = max(1, -(-word_count // 200))  # ceil division

                tokens_used = None
                if hasattr(result, "usage") and callable(result.usage):
                    try:
                        usage = result.usage()
                        tokens_used = getattr(usage, "total_tokens", None)
                    except Exception:
                        pass

                variants.append(
                    {
                        "content": content,
                        "metadata": {
                            "words": word_count,
                            "characters": char_count,
                            "readingTime": reading_time,
                            "model": model,
                            "tokens": tokens_used,
                        },
                    }
                )
            except Exception as e:
                raise Exception(f"Generation failed with {model}: {str(e)}")

        generation_time = time.time() - start_time

        return {
            "variants": variants,
            "tool_id": tool_id,
            "model_used": model,
            "generation_time": round(generation_time, 2),
        }

    async def generate_with_structured_output(
        self,
        tool_id: str,
        model: str,
        params: dict,
        tone: str = "professional",
        length: str = "medium",
        language: str = "en-US",
        creativity: float = 0.7,
    ) -> ContentVariant:
        """
        Generate content with structured output validation using Pydantic models.
        This is the recommended Pydantic AI approach for type-safe results.
        """
        ToolHandler.validate_params(tool_id, params)

        prompt = ToolHandler.build_prompt(
            tool_id=tool_id,
            params=params,
            tone=tone,
            length=length,
            language=language,
        )

        # Get the base agent for the model
        try:
            system_prompt_override = (ToolHandler.get_tool(tool_id) or {}).get("system_prompt")
            base_agent = self._get_agent_for_model(model, system_prompt=system_prompt_override)
        except ValueError as e:
            raise ValueError(str(e))

        # Create a new agent with structured output
        structured_agent = Agent(
            model=base_agent.model,
            output_type=ContentVariant,
            system_prompt=system_prompt_override or self.system_prompt,
        )

        result = await structured_agent.run(
            prompt,
            model_settings=ModelSettings(
                temperature=creativity,
                max_tokens=ToolHandler.get_max_tokens(length),
            ),
        )

        return result.output

    async def generate_stream(
        self,
        tool_id: str,
        model: str,
        params: dict,
        tone: str = "professional",
        length: str = "medium",
        language: str = "en-US",
        creativity: float = 0.7,
    ):
        """
        Generate content with streaming support for real-time updates.
        """
        ToolHandler.validate_params(tool_id, params)

        prompt = ToolHandler.build_prompt(
            tool_id=tool_id,
            params=params,
            tone=tone,
            length=length,
            language=language,
        )

        # Get agent for the requested model
        try:
            system_prompt_override = (ToolHandler.get_tool(tool_id) or {}).get("system_prompt")
            agent = self._get_agent_for_model(model, system_prompt=system_prompt_override)
        except ValueError as e:
            raise ValueError(str(e))

        async with agent.run_stream(
            prompt,
            model_settings=ModelSettings(
                temperature=creativity,
                max_tokens=ToolHandler.get_max_tokens(length),
            ),
        ) as response:
            async for message in response.stream_text():
                yield message
