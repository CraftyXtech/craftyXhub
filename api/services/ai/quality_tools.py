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

SEO_TITLE_MIN = 45
SEO_TITLE_MAX = 65
SEO_DESCRIPTION_MIN = 110
SEO_DESCRIPTION_MAX = 155


def _contains_any_phrase(text: str, phrases: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


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
    issues: list[str] = []
    seo_title = blog_post.seo_title.strip()
    seo_description = blog_post.seo_description.strip()
    hero_image_prompt = (blog_post.hero_image_prompt or "").strip()

    if not (SEO_TITLE_MIN <= len(seo_title) <= SEO_TITLE_MAX):
        issues.append(
            f"seo_title should be between {SEO_TITLE_MIN}-{SEO_TITLE_MAX} characters."
        )

    if not (SEO_DESCRIPTION_MIN <= len(seo_description) <= SEO_DESCRIPTION_MAX):
        issues.append(
            "seo_description should be between "
            f"{SEO_DESCRIPTION_MIN}-{SEO_DESCRIPTION_MAX} characters."
        )

    if not hero_image_prompt:
        issues.append(
            "Provide hero_image_prompt for a clean 1200x630 social image."
        )
    else:
        if not _contains_any_phrase(
            hero_image_prompt,
            ("1200x630", "1.91:1", "1.91 to 1", "social card"),
        ):
            issues.append(
                "hero_image_prompt should specify a 1200x630 landscape composition."
            )
        if not _contains_any_phrase(
            hero_image_prompt,
            ("no logos", "without logos", "avoid logos"),
        ):
            issues.append("hero_image_prompt should explicitly avoid logos.")
        if not _contains_any_phrase(
            hero_image_prompt,
            ("no watermarks", "without watermarks", "avoid watermarks"),
        ):
            issues.append("hero_image_prompt should explicitly avoid watermarks.")
        if not _contains_any_phrase(
            hero_image_prompt,
            ("no text overlay", "no text", "without text overlay"),
        ):
            issues.append("hero_image_prompt should explicitly avoid text overlays.")

    if not keywords:
        return issues

    primary = keywords[0].strip().lower() if keywords and keywords[0] else ""
    if not primary:
        return issues

    if primary not in seo_title.lower():
        issues.append("Primary keyword should appear in seo_title.")

    if primary not in seo_description.lower():
        issues.append("Primary keyword should appear in seo_description.")

    return issues
