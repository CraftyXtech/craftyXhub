from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic import BaseModel, Field
from core.config import settings
from .templates import TemplateHandler
import time
from typing import Dict, List, Any, Optional


class GenerationDeps(BaseModel):
    template_id: str
    tone: str
    length: str
    language: str


class ContentVariant(BaseModel):
    content: str = Field(description="The generated content")
    word_count: int = Field(description="Number of words in the content")


class AIGeneratorService:
    def __init__(self):
        self.agents = {}

        if settings.GROK_API_KEY:
            agent = Agent(
                OpenAIModel(
                    "grok-2-1212",
                    api_key=settings.GROK_API_KEY,
                    base_url="https://api.x.ai/v1",
                ),
                result_type=str,
                system_prompt=(
                    "You are an expert content writer specializing in creating engaging, "
                    "SEO-optimized content. Follow the user's instructions precisely regarding "
                    "tone, length, and style. Generate high-quality, original content."
                ),
            )
            self.agents["grok"] = agent

        if settings.OPENAI_API_KEY:
            base_url = None
            if settings.OPENAI_API_KEY.startswith("sk-free-"):
                base_url = "https://api.chatanywhere.tech/v1"

            agent = Agent(
                OpenAIModel(
                    "gpt-3.5-turbo", api_key=settings.OPENAI_API_KEY, base_url=base_url
                ),
                result_type=str,
                system_prompt=(
                    "You are an expert content writer specializing in creating engaging, "
                    "SEO-optimized content. Follow the user's instructions precisely regarding "
                    "tone, length, and style. Generate high-quality, original content."
                ),
            )
            self.agents["openai"] = agent

        if settings.FREE_CHATGPT_TOKEN:
            agent = Agent(
                OpenAIModel(
                    "gpt-3.5-turbo",
                    api_key=settings.FREE_CHATGPT_TOKEN,
                    base_url="https://api.chatanywhere.tech/v1",
                ),
                result_type=str,
                system_prompt=(
                    "You are an expert content writer specializing in creating engaging, "
                    "SEO-optimized content. Follow the user's instructions precisely regarding "
                    "tone, length, and style. Generate high-quality, original content."
                ),
            )
            self.agents["chatgpt-free"] = agent

        if settings.FREE_DEEPSEEK_TOKEN:
            agent = Agent(
                OpenAIModel(
                    "deepseek-chat",
                    api_key=settings.FREE_DEEPSEEK_TOKEN,
                    base_url="https://api.chatanywhere.tech/v1",
                ),
                result_type=str,
                system_prompt=(
                    "You are an expert content writer specializing in creating engaging, "
                    "SEO-optimized content. Follow the user's instructions precisely regarding "
                    "tone, length, and style. Generate high-quality, original content."
                ),
            )
            self.agents["deepseek-free"] = agent

        if settings.GEMINI_API_KEY:
            agent = Agent(
                GeminiModel("gemini-2.0-flash-exp", api_key=settings.GEMINI_API_KEY),
                result_type=str,
                system_prompt=(
                    "You are an expert content writer specializing in creating engaging, "
                    "SEO-optimized content. Follow the user's instructions precisely regarding "
                    "tone, length, and style. Generate high-quality, original content."
                ),
            )
            self.agents["gemini"] = agent

    async def generate(
        self,
        template_id: str,
        model: str,
        params: dict,
        tone: str = "professional",
        length: str = "medium",
        language: str = "en-US",
        creativity: float = 0.7,
        variant_count: int = 1,
    ) -> Dict[str, Any]:
        start_time = time.time()

        TemplateHandler.validate_params(template_id, params)

        prompt = TemplateHandler.build_prompt(
            template_id=template_id,
            params=params,
            tone=tone,
            length=length,
            language=language,
        )

        if model not in self.agents:
            available = list(self.agents.keys())
            if not available:
                raise ValueError(
                    "No AI models configured. Please add API keys to .env file"
                )
            raise ValueError(
                f"Model '{model}' not configured. Available models: {available}"
            )

        agent = self.agents[model]
        variants = []

        for _ in range(variant_count):
            try:
                result = await agent.run(
                    prompt,
                    model_settings={
                        "temperature": creativity,
                        "max_tokens": TemplateHandler.get_max_tokens(length),
                    },
                )

                content = result.data
                word_count = len(content.split())

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
            "template_id": template_id,
            "model_used": model,
            "generation_time": round(generation_time, 2),
        }

    async def generate_with_structured_output(
        self,
        template_id: str,
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
        TemplateHandler.validate_params(template_id, params)

        prompt = TemplateHandler.build_prompt(
            template_id=template_id,
            params=params,
            tone=tone,
            length=length,
            language=language,
        )

        if model not in self.agents:
            raise ValueError(f"Model {model} not configured")

        structured_agent = Agent(
            self.agents[model].model,
            result_type=ContentVariant,
            system_prompt=self.agents[model].system_prompt,
        )

        result = await structured_agent.run(
            prompt,
            model_settings={
                "temperature": creativity,
                "max_tokens": TemplateHandler.get_max_tokens(length),
            },
        )

        return result.data

    async def generate_stream(
        self,
        template_id: str,
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
        TemplateHandler.validate_params(template_id, params)

        prompt = TemplateHandler.build_prompt(
            template_id=template_id,
            params=params,
            tone=tone,
            length=length,
            language=language,
        )

        if model not in self.agents:
            raise ValueError(f"Model {model} not configured")

        agent = self.agents[model]

        async with agent.run_stream(
            prompt,
            model_settings={
                "temperature": creativity,
                "max_tokens": TemplateHandler.get_max_tokens(length),
            },
        ) as response:
            async for message in response.stream_text():
                yield message
