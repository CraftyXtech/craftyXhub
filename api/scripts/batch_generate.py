#!/usr/bin/env python3
"""
Generate and publish knowledge-base articles from article-topics markdown files.

Run from the repo root or api directory:
    api/venv/bin/python api/scripts/batch_generate.py --category ai --limit 5
    venv/bin/python scripts/batch_generate.py --category ai --limit 5
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

from sqlalchemy import select

API_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = API_ROOT.parent
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from database.connection import AsyncSessionLocal, close_db
from models import Post, User
from models.user import UserRole
from schemas.post import PostCreate
from services.ai.blog_agent import BlogAgentService
from services.ai.llm_config import DEFAULT_MODEL
from services.ai.seo_keywords import resolve_seo_keywords
from services.ai.taxonomy import BlogTaxonomyService
from services.post import PostService
from services.unsplash_service import UnsplashService


TOPIC_RE = re.compile(r"^\s*\d+\.\s+(.+?)\s*$")
HEADING_RE = re.compile(r"^##\s+\d+\.\s+(.+?)\s*$")

TOPIC_FILES = {
    "ai": REPO_ROOT / "article-topics" / "ai" / "ai-knowledge-base-topics.md",
    "web3": REPO_ROOT / "article-topics" / "web3-blockchain-crypto" / "web3-blockchain-knowledge-base-topics.md",
    "business": REPO_ROOT / "article-topics" / "business-finance" / "business-finance-knowledge-base-topics.md",
    "wellness": REPO_ROOT / "article-topics" / "wellness-living" / "wellness-living-knowledge-base-topics.md",
}

DEFAULT_CATEGORY_BY_FILE = {
    "ai": 45,
    "web3": 46,
    "business": 50,
    "wellness": 62,
}

SECTION_CATEGORY_MAP = {
    "ai": {
        "default": 45,
    },
    "web3": {
        "default": 46,
    },
    "business": {
        "entrepreneurship": 51,
        "startup": 51,
        "personal finance": 52,
        "wealth": 52,
        "business strategy": 53,
        "marketing": 53,
        "creator": 53,
        "online business": 53,
        "career": 57,
        "professional development": 57,
        "skill": 57,
        "default": 50,
    },
    "wellness": {
        "mental health": 63,
        "wellbeing": 63,
        "wellness": 63,
        "personal growth": 64,
        "lifestyle": 64,
        "intentional living": 64,
        "productivity": 59,
        "remote work": 59,
        "default": 62,
    },
}

IMAGE_FALLBACK_BY_CATEGORY = {
    45: "artificial intelligence technology",
    46: "blockchain cryptocurrency",
    47: "automation technology",
    48: "software development",
    49: "cybersecurity privacy",
    50: "business finance",
    51: "startup business",
    52: "personal finance",
    53: "business marketing",
    57: "professional career",
    59: "workspace productivity",
    62: "wellness lifestyle",
    63: "mental health wellbeing",
    64: "personal growth lifestyle",
}


@dataclass(frozen=True)
class TopicItem:
    key: str
    file_key: str
    source_file: Path
    source_index: int
    topic: str
    category_id: int
    section: str


def build_publish_excerpt(blog_post, html_content: str) -> str:
    summary = PostService.normalize_excerpt(blog_post.summary) or ""
    legacy_candidates = PostService.build_legacy_excerpt_candidates(
        html_content,
        None,
    )
    if summary and summary not in legacy_candidates:
        return summary

    section_headings = [section.heading.strip() for section in blog_post.sections if section.heading.strip()]
    heading_text = ", ".join(section_headings[:3])
    parts = [summary.rstrip(".")] if summary else []
    if heading_text:
        parts.append(f"Covers {heading_text}.")

    excerpt = " ".join(part for part in parts if part).strip()
    excerpt = PostService.normalize_excerpt(excerpt) or summary
    if excerpt and excerpt not in legacy_candidates:
        return excerpt

    fallback = (
        f"{blog_post.title}. This article explains the core ideas, practical uses, "
        f"and key distinctions readers need to understand the topic with confidence."
    )
    return PostService.normalize_excerpt(fallback) or blog_post.title


def parse_topics(file_key: str, path: Path) -> list[TopicItem]:
    if not path.exists():
        return []

    current_section = ""
    items: list[TopicItem] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        heading_match = HEADING_RE.match(line)
        if heading_match:
            current_section = heading_match.group(1).strip()
            continue

        topic_match = TOPIC_RE.match(line)
        if not topic_match:
            continue

        topic = topic_match.group(1).strip()
        if not topic or topic.lower().startswith("id "):
            continue

        category_id = resolve_category_id(file_key, current_section)
        source_index = len(items)
        items.append(
            TopicItem(
                key=f"{file_key}:{source_index}:{topic}",
                file_key=file_key,
                source_file=path,
                source_index=source_index,
                topic=topic,
                category_id=category_id,
                section=current_section,
            )
        )

    return items


def resolve_category_id(file_key: str, section: str) -> int:
    mapping = SECTION_CATEGORY_MAP.get(file_key, {})
    section_text = section.lower()
    for token, category_id in mapping.items():
        if token != "default" and token in section_text:
            return category_id
    return mapping.get("default", DEFAULT_CATEGORY_BY_FILE[file_key])


def load_progress(path: Path) -> dict:
    if not path.exists():
        return {"completed": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"completed": []}
    if not isinstance(payload.get("completed"), list):
        payload["completed"] = []
    return payload


def save_progress(path: Path, progress: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(progress, indent=2, sort_keys=True), encoding="utf-8")


def append_error(path: Path, item: TopicItem, error: Exception) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "topic_key": item.key,
        "topic": item.topic,
        "category_id": item.category_id,
        "error": str(error),
        "failed_at": datetime.now(timezone.utc).isoformat(),
    }
    with path.open("a", encoding="utf-8") as error_file:
        error_file.write(json.dumps(payload, sort_keys=True) + "\n")


def filter_topics(
    categories: Iterable[str],
    *,
    start_from: int,
    limit: Optional[int],
) -> list[TopicItem]:
    selected: list[TopicItem] = []
    for file_key in categories:
        selected.extend(parse_topics(file_key, TOPIC_FILES[file_key]))

    selected = selected[start_from:]
    if limit is not None:
        selected = selected[:limit]
    return selected


async def resolve_author_id(session, requested_author_id: Optional[int]) -> int:
    if requested_author_id:
        return requested_author_id

    result = await session.execute(
        select(User)
        .where(User.role.in_([UserRole.SUPER_ADMIN, UserRole.ADMIN]))
        .order_by(User.id.asc())
        .limit(1)
    )
    user = result.scalar_one_or_none()
    if user:
        return user.id

    fallback = await session.execute(select(User).order_by(User.id.asc()).limit(1))
    user = fallback.scalar_one_or_none()
    if not user:
        raise RuntimeError("No author user exists in the database")
    return user.id


async def publish_item(
    session,
    item: TopicItem,
    *,
    author_id: int,
    blog_agent: BlogAgentService,
    unsplash: UnsplashService,
    word_count: str,
    creativity: float,
    dry_run: bool,
) -> str:
    seed_keywords = resolve_seo_keywords(topic=item.topic, provided_keywords=None)
    if dry_run:
        return f"dry-run:{item.topic}"

    published_posts = await PostService.get_internal_link_targets(
        session,
        category_id=item.category_id,
        limit=50,
    )
    blog_post, _, web_search_used, sources = await blog_agent.generate(
        topic=item.topic,
        blog_type="how-to",
        keywords=seed_keywords,
        audience="Curious professionals and practical learners",
        word_count=word_count,
        tone="professional",
        language="en-US",
        model=DEFAULT_MODEL,
        creativity=creativity,
        use_web_search=False,
        published_posts=published_posts,
    )

    taxonomy_suggestion = await BlogTaxonomyService.suggest_for_generated_post(
        session,
        topic=item.topic,
        blog_post=blog_post,
        keywords=seed_keywords,
        preferred_category_id=item.category_id,
    )
    resolved_keywords = resolve_seo_keywords(
        topic=item.topic,
        provided_keywords=seed_keywords,
        blog_post=blog_post,
        taxonomy_suggestion=taxonomy_suggestion,
    )
    category_id = taxonomy_suggestion.category.id if taxonomy_suggestion.category else item.category_id
    tag_ids = [tag.id for tag in taxonomy_suggestion.tags[: BlogTaxonomyService.MAX_TAGS]]

    final_slug = blog_post.slug
    if await PostService.get_post_by_slug(session, final_slug, include_deleted=True):
        final_slug = await PostService.generate_unique_slug(session, blog_post.title, Post)
        blog_post.slug = final_slug

    primary_keyword = resolved_keywords[0] if resolved_keywords else item.topic
    featured_image = await unsplash.get_image_for_topic(
        primary_keyword,
        fallback_term=IMAGE_FALLBACK_BY_CATEGORY.get(category_id),
    )

    html_content = blog_agent.blog_post_to_html(blog_post)
    publish_excerpt = build_publish_excerpt(blog_post, html_content)
    body_word_count = sum(len(section.body_markdown.split()) for section in blog_post.sections)
    reading_time = max(1, body_word_count // 200)
    quality_report = blog_agent.build_quality_report(
        blog_post=blog_post,
        word_count=word_count,
        keywords=resolved_keywords,
        phase_metrics=blog_agent.get_last_phase_metrics(),
        published_posts_available=bool(published_posts),
    )

    post_data = PostCreate(
        title=blog_post.title,
        slug=final_slug,
        content=html_content,
        content_blocks={
            "batch_generation": {
                "source_file": str(item.source_file.relative_to(REPO_ROOT)),
                "source_index": item.source_index,
                "source_section": item.section,
                "topic": item.topic,
                "model": DEFAULT_MODEL,
                "use_web_search": False,
                "web_search_used": web_search_used,
                "search_sources_count": len(sources or []),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "internal_link_targets_count": len(published_posts),
                "quality_report": quality_report,
                "taxonomy_suggestion": taxonomy_suggestion.model_dump(exclude_none=True),
            }
        },
        excerpt=publish_excerpt,
        featured_image=featured_image,
        meta_title=blog_post.seo_title,
        meta_description=blog_post.seo_description,
        seo_keywords=resolved_keywords,
        category_id=category_id,
        tag_ids=tag_ids,
        reading_time=reading_time,
        is_published=True,
        is_featured=False,
    )
    created_post = await PostService.create_post(session, post_data, author_id)
    return created_post.slug


async def run_batch(args: argparse.Namespace) -> int:
    categories = list(TOPIC_FILES) if args.category == "all" else [args.category]
    topics = filter_topics(categories, start_from=args.start_from, limit=args.limit)
    progress_path = Path(args.progress_file)
    error_path = Path(args.error_file)
    progress = load_progress(progress_path)
    completed = set(progress["completed"])

    print(f"Loaded {len(topics)} candidate topics")
    if args.dry_run:
        for item in topics[:20]:
            print(f"[dry-run] {item.file_key} #{item.source_index} cat={item.category_id}: {item.topic}")
        return 0

    blog_agent = BlogAgentService()
    unsplash = UnsplashService()

    async with AsyncSessionLocal() as session:
        author_id = await resolve_author_id(session, args.author_id)
        published_count = 0
        for item in topics:
            if item.key in completed:
                continue

            try:
                slug = await publish_item(
                    session,
                    item,
                    author_id=author_id,
                    blog_agent=blog_agent,
                    unsplash=unsplash,
                    word_count=args.word_count,
                    creativity=args.creativity,
                    dry_run=False,
                )
                completed.add(item.key)
                progress["completed"] = sorted(completed)
                progress["last_completed"] = item.key
                progress["updated_at"] = datetime.now(timezone.utc).isoformat()
                save_progress(progress_path, progress)
                published_count += 1
                print(f"[published] {slug} ({published_count}/{len(topics)})")
                await asyncio.sleep(args.delay_seconds)
            except Exception as exc:
                await session.rollback()
                append_error(error_path, item, exc)
                print(f"[error] {item.topic}: {exc}")
                continue

    await close_db()
    print(f"Batch finished. Published {published_count} new posts.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate CraftyXHub article batches")
    parser.add_argument(
        "--category",
        choices=["all", *TOPIC_FILES.keys()],
        default="all",
    )
    parser.add_argument("--start-from", type=int, default=0)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--author-id", type=int, default=None)
    parser.add_argument("--word-count", choices=["short", "medium", "long", "very-long"], default="medium")
    parser.add_argument("--creativity", type=float, default=0.7)
    parser.add_argument("--delay-seconds", type=float, default=1.5)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--progress-file",
        default=str(API_ROOT / "scripts" / ".batch_progress.json"),
    )
    parser.add_argument(
        "--error-file",
        default=str(API_ROOT / "scripts" / ".batch_errors.jsonl"),
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run_batch(build_parser().parse_args())))
