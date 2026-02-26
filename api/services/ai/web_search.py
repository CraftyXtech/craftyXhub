"""
Web Search Service — DuckDuckGo-powered research for AI content generation.

Provides text and news search to give the AI agent access to fresh,
real-time information when generating blog posts and other content.
"""

import time
import logging
from typing import Optional

from ddgs import DDGS

logger = logging.getLogger(__name__)


class WebSearchService:
    """
    DuckDuckGo web search with in-memory TTL cache and rate limiting.

    Usage:
        svc = WebSearchService()
        results = svc.search_for_topic("AI trends 2026", ["machine learning"])
    """

    def __init__(
        self,
        max_results: int = 5,
        cache_ttl: int = 300,
        max_searches_per_request: int = 10,
    ):
        self._max_results = max_results
        self._cache_ttl = cache_ttl
        self._max_searches = max_searches_per_request
        self._search_count = 0
        # Simple in-memory cache: {query_key: (timestamp, results)}
        self._cache: dict[str, tuple[float, list[dict]]] = {}

    # ── Public API ──────────────────────────────────────────────────

    def search_text(self, query: str, max_results: int | None = None) -> list[dict]:
        """
        Search DuckDuckGo for web results.

        Returns list of dicts with keys: title, href, body
        """
        cache_key = f"text:{query}:{max_results or self._max_results}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._can_search():
            logger.warning("Search rate limit reached, returning empty results")
            return []

        try:
            results = DDGS().text(
                query,
                max_results=max_results or self._max_results,
            )
            self._search_count += 1
            self._set_cached(cache_key, results)
            return results
        except Exception as e:
            logger.error(f"DuckDuckGo text search failed: {e}")
            return []

    def search_news(
        self,
        query: str,
        max_results: int | None = None,
        timelimit: str = "w",
    ) -> list[dict]:
        """
        Search DuckDuckGo for recent news articles.

        Args:
            timelimit: d (day), w (week), m (month)

        Returns list of dicts with keys: date, title, body, url, image, source
        """
        cache_key = f"news:{query}:{max_results or self._max_results}:{timelimit}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._can_search():
            logger.warning("Search rate limit reached, returning empty results")
            return []

        try:
            results = DDGS().news(
                query,
                max_results=max_results or self._max_results,
                timelimit=timelimit,
            )
            self._search_count += 1
            self._set_cached(cache_key, results)
            return results
        except Exception as e:
            logger.error(f"DuckDuckGo news search failed: {e}")
            return []

    def search_for_topic(
        self,
        topic: str,
        keywords: list[str] | None = None,
        include_news: bool = True,
    ) -> dict:
        """
        High-level search combining text + news for a blog topic.

        Returns:
            {
                "text_results": [...],
                "news_results": [...],
                "sources": [{"title": ..., "url": ..., "snippet": ...}],
                "search_queries": [...]
            }
        """
        queries_used = []
        all_sources = []

        # Primary text search on the topic
        text_results = self.search_text(topic)
        queries_used.append(topic)

        # If keywords provided, search with keyword-enriched query
        if keywords:
            kw_query = f"{topic} {' '.join(keywords[:3])}"
            extra_results = self.search_text(kw_query, max_results=3)
            queries_used.append(kw_query)
            # Deduplicate by URL
            seen_urls = {r.get("href") for r in text_results}
            for r in extra_results:
                if r.get("href") not in seen_urls:
                    text_results.append(r)
                    seen_urls.add(r.get("href"))

        # News search
        news_results = []
        if include_news:
            news_results = self.search_news(topic, max_results=3, timelimit="w")
            queries_used.append(f"news:{topic}")

        # Build unified source list
        for r in text_results:
            all_sources.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
                "type": "web",
            })

        for r in news_results:
            all_sources.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("body", ""),
                "type": "news",
                "date": r.get("date"),
                "source": r.get("source"),
            })

        return {
            "text_results": text_results,
            "news_results": news_results,
            "sources": all_sources,
            "search_queries": queries_used,
        }

    def format_as_context(self, search_results: dict) -> str:
        """
        Format search results as a text block to inject into an LLM prompt.
        """
        parts = []

        text_results = search_results.get("text_results", [])
        news_results = search_results.get("news_results", [])

        if text_results:
            parts.append("\n\n--- WEB RESEARCH RESULTS ---")
            parts.append(
                "Use the following recent web search results to inform your writing. "
                "Incorporate relevant facts, statistics, and insights. "
                "Cite sources where appropriate.\n"
            )
            for i, r in enumerate(text_results[:7], 1):
                title = r.get("title", "Untitled")
                url = r.get("href", "")
                body = r.get("body", "")
                parts.append(f"[{i}] {title}")
                parts.append(f"    URL: {url}")
                parts.append(f"    {body}\n")

        if news_results:
            parts.append("\n--- RECENT NEWS ---")
            for i, r in enumerate(news_results[:5], 1):
                title = r.get("title", "Untitled")
                url = r.get("url", "")
                body = r.get("body", "")
                date = r.get("date", "")
                source = r.get("source", "")
                parts.append(f"[News {i}] {title}")
                parts.append(f"    Source: {source} | Date: {date}")
                parts.append(f"    URL: {url}")
                parts.append(f"    {body}\n")

        if parts:
            parts.append("--- END OF RESEARCH ---\n")

        return "\n".join(parts)

    def reset(self):
        """Reset search count for a new generation request."""
        self._search_count = 0

    # ── Private helpers ─────────────────────────────────────────────

    def _can_search(self) -> bool:
        return self._search_count < self._max_searches

    def _get_cached(self, key: str) -> list[dict] | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        ts, results = entry
        if time.time() - ts > self._cache_ttl:
            del self._cache[key]
            return None
        return results

    def _set_cached(self, key: str, results: list[dict]):
        self._cache[key] = (time.time(), results)
