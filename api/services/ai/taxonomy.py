import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from models import Category, Tag
from schemas.ai import (
    BlogPost,
    BlogTaxonomyCategory,
    BlogTaxonomySuggestion,
    BlogTaxonomyTag,
)


_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "from",
    "how",
    "in",
    "into",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


def _normalize_phrase(value: Optional[str]) -> str:
    return " ".join(_TOKEN_RE.findall((value or "").lower()))


def _tokenize(value: Optional[str]) -> set[str]:
    return {
        token
        for token in _TOKEN_RE.findall((value or "").lower())
        if len(token) > 1 and token not in _STOP_WORDS
    }


@dataclass
class _CategoryRecord:
    category: Category
    phrase: str
    slug_phrase: str
    tokens: set[str]


@dataclass
class _TagRecord:
    tag: Tag
    phrase: str
    slug_phrase: str
    tokens: set[str]


class BlogTaxonomyService:
    MAX_TAGS = 5
    LOW_CONFIDENCE_THRESHOLD = 0.45
    MEANINGFUL_CATEGORY_EVIDENCE = 8

    @staticmethod
    async def suggest_for_generated_post(
        session: AsyncSession | None,
        *,
        topic: str,
        blog_post: BlogPost,
        keywords: Optional[list[str]] = None,
        preferred_category_id: Optional[int] = None,
    ) -> BlogTaxonomySuggestion:
        if session is None:
            return BlogTaxonomySuggestion()

        categories_result = await session.execute(select(Category))
        tags_result = await session.execute(
            select(Tag).where(Tag.is_active.is_(True), Tag.canonical_tag_id.is_(None))
        )
        categories = categories_result.scalars().all()
        tags = tags_result.scalars().all()

        if not categories:
            return BlogTaxonomySuggestion()

        resolver = _TaxonomyResolver(categories=categories, tags=tags)
        return resolver.resolve(
            topic=topic,
            blog_post=blog_post,
            keywords=keywords,
            preferred_category_id=preferred_category_id,
        )


class _TaxonomyResolver:
    def __init__(self, *, categories: list[Category], tags: list[Tag]):
        self.categories = categories
        self.tags = tags
        self.categories_by_id = {category.id: category for category in categories}
        self.child_ids_by_parent: dict[int, set[int]] = defaultdict(set)
        for category in categories:
            if category.parent_id:
                self.child_ids_by_parent[category.parent_id].add(category.id)

        self.category_records = [
            _CategoryRecord(
                category=category,
                phrase=_normalize_phrase(category.name),
                slug_phrase=_normalize_phrase(category.slug),
                tokens=_tokenize(f"{category.name} {category.slug}"),
            )
            for category in categories
        ]
        self.tag_records = [
            _TagRecord(
                tag=tag,
                phrase=_normalize_phrase(tag.name),
                slug_phrase=_normalize_phrase(tag.slug),
                tokens=_tokenize(f"{tag.name} {tag.slug}"),
            )
            for tag in tags
        ]

    def resolve(
        self,
        *,
        topic: str,
        blog_post: BlogPost,
        keywords: Optional[list[str]],
        preferred_category_id: Optional[int],
    ) -> BlogTaxonomySuggestion:
        core_text = " ".join(
            filter(
                None,
                [
                    topic,
                    blog_post.title,
                    blog_post.summary,
                    " ".join(section.heading for section in blog_post.sections),
                    " ".join(keywords or []),
                ],
            )
        )
        generated_tag_text = " ".join(blog_post.tags or [])
        full_text = " ".join(filter(None, [core_text, generated_tag_text]))
        core_phrase = _normalize_phrase(core_text)
        core_tokens = _tokenize(core_text)
        full_phrase = _normalize_phrase(full_text)
        full_tokens = _tokenize(full_text)
        title_summary_phrase = _normalize_phrase(
            " ".join(filter(None, [topic, blog_post.title, blog_post.summary]))
        )
        title_summary_tokens = _tokenize(
            " ".join(filter(None, [topic, blog_post.title, blog_post.summary]))
        )
        keyword_phrases = {_normalize_phrase(keyword) for keyword in (keywords or []) if keyword}
        keyword_token_sets = [_tokenize(keyword) for keyword in (keywords or []) if keyword]
        ai_tag_phrases = {_normalize_phrase(tag) for tag in (blog_post.tags or []) if tag}
        ai_tag_token_sets = [_tokenize(tag) for tag in (blog_post.tags or []) if tag]

        tag_scores: dict[int, int] = {}
        for record in self.tag_records:
            score = 0

            if record.phrase and record.phrase in ai_tag_phrases:
                score += 18
            if record.slug_phrase and record.slug_phrase in ai_tag_phrases:
                score += 16

            score += self._best_overlap_bonus(record.tokens, ai_tag_token_sets, 10, 4)
            score += self._best_overlap_bonus(record.tokens, keyword_token_sets, 8, 3)

            if record.phrase and record.phrase in keyword_phrases:
                score += 14
            if record.phrase and record.phrase in title_summary_phrase:
                score += 10
            if record.slug_phrase and record.slug_phrase in title_summary_phrase:
                score += 8
            if record.phrase and record.phrase in full_phrase:
                score += 6

            overlap = len(record.tokens & full_tokens)
            score += overlap * 2
            if record.tokens and record.tokens.issubset(title_summary_tokens):
                score += 4

            if score > 0:
                tag_scores[record.tag.id] = score

        category_scores: dict[int, int] = defaultdict(int)
        category_direct_scores: dict[int, int] = defaultdict(int)
        for record in self.category_records:
            score = 0

            if record.phrase and record.phrase in title_summary_phrase:
                score += 18
            if record.slug_phrase and record.slug_phrase in title_summary_phrase:
                score += 12
            if record.phrase and record.phrase in core_phrase:
                score += 8

            overlap = len(record.tokens & core_tokens)
            score += overlap * 3

            if record.category.parent_id:
                parent = self.categories_by_id.get(record.category.parent_id)
                if parent:
                    parent_tokens = _tokenize(f"{parent.name} {parent.slug}")
                    score += len(parent_tokens & core_tokens)

            if score > 0:
                category_direct_scores[record.category.id] += score
                category_scores[record.category.id] += score

        for tag_record in self.tag_records:
            score = tag_scores.get(tag_record.tag.id)
            if not score or not tag_record.tag.category_id:
                continue

            tag_category_id = tag_record.tag.category_id
            tag_has_core_evidence = bool(
                (tag_record.phrase and tag_record.phrase in title_summary_phrase)
                or (tag_record.slug_phrase and tag_record.slug_phrase in title_summary_phrase)
                or (tag_record.phrase and tag_record.phrase in keyword_phrases)
                or (tag_record.tokens and tag_record.tokens.issubset(title_summary_tokens))
            )
            if (
                category_direct_scores.get(tag_category_id, 0)
                >= BlogTaxonomyService.MEANINGFUL_CATEGORY_EVIDENCE
                or tag_has_core_evidence
            ):
                category_scores[tag_category_id] += score * 2
            else:
                # Generated tags can be noisy. A single stray tag such as
                # "security" or "crime" should not override stronger topic,
                # title, summary, and keyword evidence for the article.
                category_scores[tag_category_id] += min(score, 8)

            parent_id = self.categories_by_id.get(tag_category_id).parent_id
            if parent_id:
                category_scores[parent_id] += min(score, 10)

        chosen_category = self._pick_category(category_scores, preferred_category_id)
        chosen_tag_records = self._pick_tags(tag_scores, chosen_category)
        confidence_score = self._calculate_confidence(
            category_scores=category_scores,
            category_direct_scores=category_direct_scores,
            tag_scores=tag_scores,
            chosen_category=chosen_category,
            chosen_tag_records=chosen_tag_records,
        )
        review_required = confidence_score < BlogTaxonomyService.LOW_CONFIDENCE_THRESHOLD

        if review_required and preferred_category_id is None:
            return BlogTaxonomySuggestion(
                confidence_score=confidence_score,
                review_required=True,
            )

        return BlogTaxonomySuggestion(
            category=self._to_category_payload(chosen_category),
            tags=[self._to_tag_payload(record.tag) for record in chosen_tag_records],
            confidence_score=confidence_score,
            review_required=review_required,
        )

    def _pick_category(
        self,
        category_scores: dict[int, int],
        preferred_category_id: Optional[int],
    ) -> Optional[Category]:
        if preferred_category_id:
            return self.categories_by_id.get(preferred_category_id)

        if not category_scores:
            return None

        chosen_id = max(
            category_scores,
            key=lambda category_id: (
                category_scores[category_id],
                bool(self.categories_by_id[category_id].parent_id),
                self.categories_by_id[category_id].id,
            ),
        )
        return self.categories_by_id.get(chosen_id)

    def _pick_tags(
        self,
        tag_scores: dict[int, int],
        chosen_category: Optional[Category],
    ) -> list[_TagRecord]:
        if not tag_scores:
            return []

        allowed_category_ids: Optional[set[int]] = None
        if chosen_category is not None:
            allowed_category_ids = {chosen_category.id}
            allowed_category_ids.update(self.child_ids_by_parent.get(chosen_category.id, set()))

        scored_records = [
            record
            for record in self.tag_records
            if record.tag.id in tag_scores
            and (
                allowed_category_ids is None
                or record.tag.category_id in allowed_category_ids
            )
        ]
        scored_records.sort(
            key=lambda record: (
                tag_scores[record.tag.id],
                bool(record.phrase),
                record.tag.id,
            ),
            reverse=True,
        )

        selected: list[_TagRecord] = []
        minimum_score = 6 if scored_records else 0
        for record in scored_records:
            if tag_scores[record.tag.id] < minimum_score and len(selected) >= 2:
                break
            selected.append(record)
            if len(selected) >= BlogTaxonomyService.MAX_TAGS:
                return selected

        if len(selected) >= BlogTaxonomyService.MAX_TAGS or not chosen_category:
            return selected

        fallback_records = [
            record
            for record in scored_records
            if record not in selected and tag_scores[record.tag.id] >= 3
        ]
        for record in fallback_records:
            selected.append(record)
            if len(selected) >= BlogTaxonomyService.MAX_TAGS:
                break

        return selected

    def _calculate_confidence(
        self,
        *,
        category_scores: dict[int, int],
        category_direct_scores: dict[int, int],
        tag_scores: dict[int, int],
        chosen_category: Optional[Category],
        chosen_tag_records: list[_TagRecord],
    ) -> float:
        if chosen_category is None and not chosen_tag_records:
            return 0.0

        category_component = 0.0
        confidence_cap: Optional[float] = None
        if chosen_category is not None:
            chosen_score = category_scores.get(chosen_category.id, 0)
            ranked_category_ids = sorted(
                category_scores,
                key=lambda category_id: (
                    category_scores[category_id],
                    bool(self.categories_by_id[category_id].parent_id),
                    self.categories_by_id[category_id].id,
                ),
                reverse=True,
            )
            runner_up_score = 0
            for category_id in ranked_category_ids:
                if category_id != chosen_category.id:
                    runner_up_score = category_scores[category_id]
                    break

            saturation = min(chosen_score / 30, 1.0)
            dominance = max(chosen_score - runner_up_score, 0) / max(chosen_score, 1)
            category_component = (saturation * 0.55) + (dominance * 0.25)

            direct_score = category_direct_scores.get(chosen_category.id, 0)
            if direct_score < BlogTaxonomyService.MEANINGFUL_CATEGORY_EVIDENCE:
                confidence_cap = BlogTaxonomyService.LOW_CONFIDENCE_THRESHOLD - 0.05

        tag_component = 0.0
        if chosen_tag_records:
            average_tag_score = sum(
                tag_scores.get(record.tag.id, 0) for record in chosen_tag_records
            ) / max(len(chosen_tag_records), 1)
            tag_component = min(average_tag_score / 18, 1.0) * 0.2

        confidence = min(category_component + tag_component, 1.0)
        if confidence_cap is not None:
            confidence = min(confidence, confidence_cap)
        return round(confidence, 2)

    @staticmethod
    def _best_overlap_bonus(
        tag_tokens: set[str],
        candidate_token_sets: list[set[str]],
        base_bonus: int,
        per_token_bonus: int,
    ) -> int:
        best = 0
        for candidate_tokens in candidate_token_sets:
            overlap = len(tag_tokens & candidate_tokens)
            if overlap:
                best = max(best, base_bonus + (overlap * per_token_bonus))
        return best

    @staticmethod
    def _to_category_payload(category: Optional[Category]) -> Optional[BlogTaxonomyCategory]:
        if category is None:
            return None
        return BlogTaxonomyCategory(
            id=category.id,
            name=category.name,
            slug=category.slug,
            parent_id=category.parent_id,
        )

    @staticmethod
    def _to_tag_payload(tag: Tag) -> BlogTaxonomyTag:
        return BlogTaxonomyTag(
            id=tag.id,
            name=tag.name,
            slug=tag.slug,
            category_id=tag.category_id,
        )
