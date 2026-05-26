import logging
from typing import Optional

import httpx

from core.config import settings

logger = logging.getLogger(__name__)


class UnsplashService:
    SEARCH_URL = "https://api.unsplash.com/search/photos"
    DEFAULT_FALLBACK_TERMS = {
        # Tech & Innovation
        "ai": "technology",
        "artificial intelligence": "technology",
        "machine learning": "technology",
        "automation": "technology",
        "software": "code programming",
        "cybersecurity": "cybersecurity digital security",
        "privacy": "cybersecurity privacy",
        # Blockchain & Crypto
        "blockchain": "blockchain technology",
        "crypto": "cryptocurrency",
        "bitcoin": "cryptocurrency",
        # Business & Finance
        "finance": "business finance",
        "business": "business",
        "startup": "startup business",
        "entrepreneurship": "startup business",
        "marketing": "business marketing",
        "career": "professional career",
        # Global Issues
        "conflict": "editorial conflict war",
        "war": "editorial conflict military",
        "diplomacy": "editorial diplomacy international",
        "politics": "editorial politics government",
        "governance": "editorial politics government",
        "security": "editorial security defense",
        "intelligence": "editorial security",
        "international": "editorial international diplomacy",
        "energy": "editorial energy oil",
        "climate": "editorial climate environment",
        "global": "editorial world affairs",
        # Wellness
        "wellness": "wellness",
        "mental health": "wellness mental health",
        "productivity": "workspace productivity",
        "lifestyle": "lifestyle personal growth",
    }

    def __init__(
        self,
        access_key: Optional[str] = None,
        timeout_seconds: float = 10.0,
    ):
        self.access_key = access_key if access_key is not None else settings.UNSPLASH_ACCESS_KEY
        self.timeout_seconds = timeout_seconds

    async def get_image_for_topic(
        self,
        keyword: str,
        fallback_term: Optional[str] = None,
    ) -> str | None:
        if not self.access_key:
            logger.info("Skipping Unsplash lookup because UNSPLASH_ACCESS_KEY is not configured")
            return None

        query = self._clean_query(keyword)
        fallback_query = self._clean_query(
            fallback_term or self._fallback_for_query(query)
        )

        for candidate in dict.fromkeys([query, fallback_query]):
            if not candidate:
                continue

            try:
                image_url = await self._search_best_image(candidate)
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 403:
                    logger.warning("Unsplash limit or authorization issue; publishing without image")
                    return None
                logger.warning("Unsplash lookup failed for %s: %s", candidate, exc)
                continue
            except httpx.HTTPError as exc:
                logger.warning("Unsplash request failed for %s: %s", candidate, exc)
                continue

            if image_url:
                return image_url

        return None

    async def _search_best_image(self, query: str) -> str | None:
        """Fetch up to 10 results and pick the best one by quality scoring."""
        headers = {"Authorization": f"Client-ID {self.access_key}"}
        params = {
            "query": query,
            "per_page": 10,
            "page": 1,
            "order_by": "relevant",
            "orientation": "landscape",
            "content_filter": "high",
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(self.SEARCH_URL, headers=headers, params=params)
            response.raise_for_status()
            payload = response.json()

        results = payload.get("results") or []
        if not results:
            return None

        query_lower = query.lower()
        query_tokens = set(query_lower.split())

        def score_image(photo: dict) -> int:
            score = 0
            desc = photo.get("description") or ""
            alt = photo.get("alt_description") or ""

            # Strongly prefer images with descriptions (editorial/curated)
            if desc.strip():
                score += 3
            if alt.strip():
                score += 2

            # Bonus if description contains query terms (better relevance)
            desc_text = (desc + " " + alt).lower()
            matching_tokens = sum(1 for t in query_tokens if t in desc_text)
            score += matching_tokens

            # Likes as tiebreaker (capped at 5)
            likes = photo.get("likes") or 0
            score += min(likes // 10, 5)

            # Tags relevance bonus
            tags = photo.get("tags") or []
            for tag in tags:
                tag_title = (tag.get("title") or "").lower()
                if any(t in tag_title for t in query_tokens):
                    score += 1

            return score

        results.sort(key=score_image, reverse=True)
        best = results[0]

        urls = best.get("urls") or {}
        logger.info(
            "Unsplash: query=%s picked score=%d likes=%d has_desc=%s",
            query, score_image(best), best.get("likes") or 0,
            bool(best.get("description")),
        )
        return urls.get("regular")

    @classmethod
    def _fallback_for_query(cls, query: str) -> str:
        lowered = query.lower()
        for token, fallback in cls.DEFAULT_FALLBACK_TERMS.items():
            if token in lowered:
                return fallback
        return "editorial technology"

    @staticmethod
    def _clean_query(value: Optional[str]) -> str:
        return " ".join(str(value or "").split())[:120]
