import json
import re
from dataclasses import dataclass
from datetime import datetime
from html import escape, unescape
from pathlib import PurePosixPath
from urllib.parse import quote

from fastapi import Request

from core.config import settings
from models import Post


@dataclass(frozen=True)
class SharePageContext:
    title: str
    description: str
    canonical_url: str
    share_url: str
    image_url: str
    image_alt: str
    site_name: str
    published_time: str | None
    author_name: str | None


class SharePageService:
    SITE_NAME = "CraftyXHub"
    DEFAULT_DESCRIPTION = "Read this article on CraftyXHub."
    DESCRIPTION_MAX_LENGTH = 220

    @classmethod
    def build_post_context(cls, request: Request, post: Post) -> SharePageContext:
        title = cls._resolve_title(post)
        description = cls._resolve_description(post)
        canonical_url = cls._build_frontend_post_url(post.slug)
        share_url = str(request.url)
        image_url = cls._resolve_image_url(request, post.featured_image)
        image_alt = post.title or title or cls.SITE_NAME
        author_name = (
            post.author.full_name
            if getattr(post, "author", None) and getattr(post.author, "full_name", None)
            else None
        )
        published_time = cls._format_datetime(post.published_at or post.created_at)

        return SharePageContext(
            title=title,
            description=description,
            canonical_url=canonical_url,
            share_url=share_url,
            image_url=image_url,
            image_alt=image_alt,
            site_name=getattr(settings, "SITE_NAME", cls.SITE_NAME) or cls.SITE_NAME,
            published_time=published_time,
            author_name=author_name,
        )

    @classmethod
    def render_post_html(cls, context: SharePageContext) -> str:
        title = escape(context.title, quote=True)
        description = escape(context.description, quote=True)
        canonical_url = escape(context.canonical_url, quote=True)
        share_url = escape(context.share_url, quote=True)
        image_url = escape(context.image_url, quote=True)
        image_alt = escape(context.image_alt, quote=True)
        site_name = escape(context.site_name, quote=True)
        body_title = escape(context.title)
        body_description = escape(context.description)
        redirect_url_json = json.dumps(context.canonical_url)

        published_meta = ""
        if context.published_time:
            published_time = escape(context.published_time, quote=True)
            published_meta = (
                f'\n    <meta property="article:published_time" content="{published_time}" />'
            )

        author_meta = ""
        if context.author_name:
            author_name = escape(context.author_name, quote=True)
            author_meta = f'\n    <meta property="article:author" content="{author_name}" />'

        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <meta name="description" content="{description}" />
    <meta name="robots" content="noindex,follow,max-image-preview:large" />
    <meta http-equiv="refresh" content="3;url={canonical_url}" />
    <link rel="canonical" href="{canonical_url}" />

    <meta property="og:site_name" content="{site_name}" />
    <meta property="og:type" content="article" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:url" content="{share_url}" />
    <meta property="og:image" content="{image_url}" />
    <meta property="og:image:alt" content="{image_alt}" />{published_meta}{author_meta}

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{description}" />
    <meta name="twitter:image" content="{image_url}" />

    <style>
      :root {{
        color-scheme: light;
        --bg: #f5f7fb;
        --card: #ffffff;
        --ink: #122033;
        --muted: #54657d;
        --accent: #0f6cbd;
        --border: #d8e0ea;
      }}

      * {{
        box-sizing: border-box;
      }}

      body {{
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        padding: 24px;
        background: radial-gradient(circle at top, #ffffff 0%, var(--bg) 65%);
        color: var(--ink);
        font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }}

      main {{
        width: min(640px, 100%);
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 28px;
        box-shadow: 0 20px 60px rgba(18, 32, 51, 0.08);
      }}

      .eyebrow {{
        margin: 0 0 12px;
        color: var(--muted);
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }}

      h1 {{
        margin: 0 0 12px;
        font-size: clamp(28px, 4vw, 40px);
        line-height: 1.08;
      }}

      p {{
        margin: 0;
        color: var(--muted);
        font-size: 16px;
        line-height: 1.6;
      }}

      a {{
        display: inline-flex;
        margin-top: 20px;
        align-items: center;
        gap: 8px;
        padding: 12px 18px;
        border-radius: 999px;
        background: var(--accent);
        color: #ffffff;
        text-decoration: none;
        font-weight: 600;
      }}
    </style>

    <script>
      window.location.replace({redirect_url_json});
    </script>
  </head>
  <body>
    <main>
      <p class="eyebrow">Opening Article</p>
      <h1>{body_title}</h1>
      <p>{body_description}</p>
      <a href="{canonical_url}">Continue reading on {escape(context.site_name)}</a>
    </main>
  </body>
</html>
"""

    @classmethod
    def _resolve_title(cls, post: Post) -> str:
        return (post.meta_title or post.title or cls.SITE_NAME).strip()

    @classmethod
    def _resolve_description(cls, post: Post) -> str:
        for candidate in (post.meta_description, post.excerpt, cls._extract_plain_text(post.content)):
            normalized = cls._normalize_text(candidate)
            if normalized:
                return cls._truncate(normalized, cls.DESCRIPTION_MAX_LENGTH)
        return cls.DEFAULT_DESCRIPTION

    @classmethod
    def _resolve_image_url(cls, request: Request, image_path: str | None) -> str:
        if image_path:
            trimmed = image_path.strip()
            if trimmed.startswith(("http://", "https://")):
                return trimmed

            pure_path = PurePosixPath(trimmed)
            filename = pure_path.name
            folder = pure_path.parent.name or "posts"
            base_url = str(request.url_for("get_image", filename=filename))
            return f"{base_url}?folder={quote(folder, safe='')}"

        default_image_url = getattr(settings, "DEFAULT_SHARE_IMAGE_URL", "") or ""
        if default_image_url:
            return default_image_url

        return f"{settings.FRONTEND_URL.rstrip('/')}/logo.png"

    @staticmethod
    def _build_frontend_post_url(slug: str) -> str:
        return f"{settings.FRONTEND_URL.rstrip('/')}/post/{quote(slug, safe='')}"

    @staticmethod
    def _extract_plain_text(content: str | None) -> str:
        if not content:
            return ""
        plain_text = re.sub(r"<[^>]+>", " ", content)
        return unescape(plain_text)

    @staticmethod
    def _normalize_text(value: str | None) -> str:
        if not value:
            return ""
        return re.sub(r"\s+", " ", value).strip()

    @staticmethod
    def _truncate(value: str, limit: int) -> str:
        if len(value) <= limit:
            return value
        truncated = value[: limit - 3].rsplit(" ", 1)[0].strip()
        return f"{truncated or value[: limit - 3].strip()}..."

    @staticmethod
    def _format_datetime(value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()
