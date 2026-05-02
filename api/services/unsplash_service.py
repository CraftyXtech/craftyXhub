import logging
from typing import Optional

import httpx

from core.config import settings

logger = logging.getLogger(__name__)


class UnsplashService:
    SEARCH_URL = "https://api.unsplash.com/search/photos"
    DEFAULT_FALLBACK_TERMS = {
        "ai": "technology",
        "artificial intelligence": "technology",
        "machine learning": "technology",
        "blockchain": "blockchain technology",
        "crypto": "cryptocurrency",
        "finance": "business finance",
        "business": "business",
        "startup": "startup business",
        "wellness": "wellness",
        "mental health": "wellness",
        "productivity": "workspace productivity",
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
                image_url = await self._search_first_image(candidate)
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

    async def _search_first_image(self, query: str) -> str | None:
        headers = {"Authorization": f"Client-ID {self.access_key}"}
        params = {
            "query": query,
            "per_page": 1,
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

        urls = results[0].get("urls") or {}
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
