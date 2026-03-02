import re
from typing import Optional

from schemas.ai import BlogPost


_AI_TROPE_PHRASES = [
    "delve into",
    "in the realm of",
    "it is worth noting",
    "leverage",
    "game changer",
    "groundbreaking",
    "seamlessly",
    "cutting-edge",
    "paramount",
    "comprehensive guide",
]


def extract_blog_plaintext(blog_post: BlogPost) -> str:
    sections_text = "\n\n".join(section.body_markdown for section in blog_post.sections)
    return f"{blog_post.title}\n\n{blog_post.summary}\n\n{sections_text}".strip()


def find_ai_tropes(text: str) -> list[str]:
    lowered = text.lower()
    return [phrase for phrase in _AI_TROPE_PHRASES if phrase in lowered]


def analyze_readability(text: str) -> dict:
    try:
        import textstat  # type: ignore

        ease = float(textstat.flesch_reading_ease(text))
        grade = float(textstat.flesch_kincaid_grade(text))
        return {
            "flesch_reading_ease": ease,
            "flesch_kincaid_grade": grade,
            "is_hard_to_read": ease < 30 or grade > 14,
            "reason": "textstat",
        }
    except Exception:
        words = re.findall(r"\b\w+\b", text)
        sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]

        # If punctuation is sparse, avoid over-enforcing readability.
        if len(sentences) < 3:
            return {
                "flesch_reading_ease": None,
                "flesch_kincaid_grade": None,
                "is_hard_to_read": False,
                "reason": "insufficient_sentence_markers",
            }

        avg_sentence_words = len(words) / max(1, len(sentences))
        return {
            "flesch_reading_ease": None,
            "flesch_kincaid_grade": None,
            "is_hard_to_read": avg_sentence_words > 28,
            "reason": "heuristic",
        }


def seo_quality_issues(blog_post: BlogPost, keywords: Optional[list[str]]) -> list[str]:
    if not keywords:
        return []

    issues: list[str] = []
    primary = keywords[0].strip().lower() if keywords and keywords[0] else ""
    if not primary:
        return issues

    if primary not in blog_post.seo_title.lower():
        issues.append("Primary keyword should appear in seo_title.")

    if primary not in blog_post.seo_description.lower():
        issues.append("Primary keyword should appear in seo_description.")

    return issues
