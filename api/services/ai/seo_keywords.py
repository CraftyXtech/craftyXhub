from __future__ import annotations

import re
from typing import Iterable

from schemas.ai import BlogPost, BlogTaxonomySuggestion


MAX_SEO_KEYWORDS = 6
_ACRONYMS = {"ai", "api", "aws", "gdp", "ipo", "llm", "llms", "seo", "sql", "ui", "uk", "un", "us", "ux"}
_STOPWORDS = {
    "a",
    "an",
    "and",
    "article",
    "for",
    "how",
    "in",
    "news",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


def _clean_phrase(value: str) -> str:
    phrase = re.sub(r"\s+", " ", value or "").strip()
    phrase = phrase.strip(".,:;|/-()[]{} ")
    return phrase


def _canonical_key(value: str) -> str:
    canonical = _clean_phrase(value).lower()
    canonical = canonical.replace("&", "and")
    canonical = re.sub(r"[^a-z0-9\s]", "", canonical)
    canonical = re.sub(r"\s+", " ", canonical).strip()
    return canonical


def _display_phrase(value: str) -> str:
    words = re.split(r"\s+", _clean_phrase(value).replace("-", " "))
    display_words: list[str] = []
    for word in words:
        lower = word.lower()
        if not lower:
            continue
        if lower in _ACRONYMS:
            display_words.append(lower.upper())
        elif lower.isdigit():
            display_words.append(lower)
        else:
            display_words.append(lower.capitalize())
    return " ".join(display_words)


def _looks_useful(phrase: str) -> bool:
    canonical = _canonical_key(phrase)
    if not canonical:
        return False
    if canonical in _STOPWORDS:
        return False
    words = canonical.split()
    if len(words) > 10:
        return False
    if len(words) == 1 and len(words[0]) < 3:
        return False
    return True


def _extract_candidate_phrases(text: str) -> list[str]:
    cleaned = _clean_phrase(text)
    if not cleaned:
        return []

    raw_candidates = [cleaned.replace("-", " ")]
    raw_candidates.extend(
        part.replace("-", " ")
        for part in re.split(r"\s*[:,;|/]\s*", cleaned)
    )

    candidates: list[str] = []
    for candidate in raw_candidates:
        normalized = _clean_phrase(candidate)
        if _looks_useful(normalized):
            candidates.append(normalized)
    return candidates


def _iter_seed_terms(values: Iterable[str] | None) -> Iterable[str]:
    for value in values or []:
        if value and value.strip():
            yield value


def resolve_seo_keywords(
    *,
    topic: str,
    provided_keywords: list[str] | None = None,
    blog_post: BlogPost | None = None,
    taxonomy_suggestion: BlogTaxonomySuggestion | None = None,
) -> list[str]:
    resolved: list[str] = []
    seen: set[str] = set()

    def add_phrase(phrase: str) -> None:
        if len(resolved) >= MAX_SEO_KEYWORDS:
            return
        canonical = _canonical_key(phrase)
        if not canonical or canonical in seen:
            return
        if not _looks_useful(phrase):
            return
        resolved.append(_display_phrase(phrase))
        seen.add(canonical)

    def add_source(source: str) -> None:
        for phrase in _extract_candidate_phrases(source):
            add_phrase(phrase)
            if len(resolved) >= MAX_SEO_KEYWORDS:
                return

    for keyword in _iter_seed_terms(provided_keywords):
        add_source(keyword)

    add_source(topic)

    if blog_post is not None:
        add_source(blog_post.title)
        for tag in _iter_seed_terms(blog_post.tags):
            add_source(tag)

    if taxonomy_suggestion is not None:
        if taxonomy_suggestion.category is not None:
            add_source(taxonomy_suggestion.category.name)
        for tag in taxonomy_suggestion.tags:
            add_source(tag.name)

    return resolved[:MAX_SEO_KEYWORDS]
