class ToolHandler:
    TOOLS = {
        "blog-ideas": {
            "prompt": """Generate blog post ideas about {category}.
Keywords: {keywords}
Tone: {tone}
Target audience: {audience}

Format as a numbered list with title and brief description.""",
            "required_fields": ["category", "keywords"],
            "optional_fields": ["audience"]
        },
        "outline-generator": {
            "prompt": """Create a detailed blog outline for: {title}
Keywords: {keywords}
Number of sections: {sections}
Tone: {tone}

Include H2/H3 headings, talking points, and CTAs.""",
            "required_fields": ["title", "keywords"],
            "optional_fields": ["sections"]
        },
        "section-draft": {
            "prompt": """Write a section based on this outline:
{outline}
Tone: {tone}

Write engaging, well-structured content.""",
            "required_fields": ["outline"]
        },
        "title-variants": {
            "prompt": """Generate headline variants for the topic: {topic}
Keywords: {keywords}
Style: {style}
Tone: {tone}

Create 5-7 compelling headline options with brief scoring notes.""",
            "required_fields": ["topic", "keywords"],
            "optional_fields": ["style"]
        },
        "intro-conclusion-cta": {
            "prompt": """Create introduction, conclusion, and CTA for: {title}
Summary: {summary}
CTA goal: {cta_goal}
Tone: {tone}

Provide engaging hooks, closers, and targeted CTAs.""",
            "required_fields": ["title", "summary", "cta_goal"]
        },
        "seo-pack": {
            "prompt": """Generate SEO pack for this content:
{content}
Focus keyword: {focus_keyword}
Target audience: {audience}
Tone: {tone}

Include: meta title (60 chars), meta description (160 chars), slug, keywords list, and FAQ schema suggestions.""",
            "required_fields": ["content", "focus_keyword"],
            "optional_fields": ["audience"]
        },
        "image-alt-text": {
            "prompt": """Generate alt text and captions for images in this context:
{image_context}
Caption style: {caption_style}
Tone: {tone}

Provide SEO-friendly alt tags and engaging captions.""",
            "required_fields": ["image_context"],
            "optional_fields": ["caption_style"]
        },
        "internal-link-suggester": {
            "prompt": """Suggest internal links for this content:
{content}
Available slugs: {available_slugs}
Tone: {tone}

Provide anchor text suggestions and optimal placement.""",
            "required_fields": ["content", "available_slugs"]
        },
        "content-refiner": {
            "prompt": """Refine this content:
{content}
Tone: {tone}
Style: {style}

Rewrite to improve clarity, engagement, and readability. Options: simplify, expand, or remove jargon.""",
            "required_fields": ["content"],
            "optional_fields": ["style"]
        },
        "summarizer-brief": {
            "prompt": """Create a concise summary/brief from:
{content}
Tone: {tone}

Extract key points and create a professional brief.""",
            "required_fields": ["content"]
        },
        "fact-checklist": {
            "prompt": """Review this content for fact-checking:
{content}
Tone: {tone}

Highlight claims needing sources and suggest disclaimers where appropriate.""",
            "required_fields": ["content"]
        },
        "style-adapter": {
            "prompt": """Adapt this content to the specified style:
{content}
Target tone: {tone}
Reading level: {reading_level}
Tone: {tone}

Rewrite to match brand voice and reading level.""",
            "required_fields": ["content"],
            "optional_fields": ["reading_level"]
        }
    }
    
    @staticmethod
    def build_prompt(
        tool_id: str,
        params: dict,
        tone: str,
        length: str,
        language: str,
        prompt: str | None = None,
        keywords: list[str] | str | None = None,
    ) -> str:
        """Build a prompt either from a known tool with required params
        or fall back to a generic prompt using the provided freeform prompt/keywords.
        """
        tool = ToolHandler.TOOLS.get(tool_id)
        length_map = {
            "short": "50-100 words",
            "medium": "100-300 words",
            "long": "300-500 words",
            "very-long": "500+ words",
        }

        # If we have a valid tool and params likely satisfy, render it
        if tool:
            filled_params = {"tone": tone, **params}
            for field in tool.get("optional_fields", []):
                if field not in filled_params:
                    filled_params[field] = "Not specified"
            try:
                base = tool["prompt"].format(**filled_params)
                result = base + f"\n\nLength: {length_map.get(length, '100-300 words')}"
                if language != "en-US":
                    result += f"\n\nWrite in {language}."
                return result
            except KeyError:
                # Fall back to generic below if fields are missing
                pass

        # Generic fallback using freeform prompt
        if not prompt:
            raise ValueError(
                f"Tool {tool_id} requires additional fields or a freeform prompt."
            )

        kw_text = (
            ", ".join(keywords) if isinstance(keywords, list) else (keywords or "")
        )
        generic = [
            "You are an expert content writer creating engaging, SEO-optimized content.",
            f"Tone: {tone}",
            f"Target length: {length_map.get(length, '100-300 words')}",
        ]
        if language != "en-US":
            generic.append(f"Language: {language}")
        if kw_text:
            generic.append(f"Primary keywords: {kw_text}")
        generic.append("Instructions:")
        generic.append(prompt)
        return "\n".join(generic)
    
    @staticmethod
    def get_max_tokens(length: str) -> int:
        return {
            "short": 200,
            "medium": 600,
            "long": 1000,
            "very-long": 2000
        }.get(length, 600)
    
    @staticmethod
    def validate_params(tool_id: str, params: dict) -> None:
        tool = ToolHandler.TOOLS.get(tool_id)
        if not tool:
            raise ValueError(f"Tool {tool_id} not found")
        
        required = tool["required_fields"]
        missing = [f for f in required if f not in params or not params[f]]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

