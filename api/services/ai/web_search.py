"""
Web Search Service — DuckDuckGo-powered research for AI content generation.

Provides text and news search to give the AI agent access to fresh,
real-time information when generating blog posts and other content.
"""

import contextlib
import io
import logging
import time
from typing import Optional

import primp
from ddgs import DDGS
from ddgs.exceptions import DDGSException
from ddgs.http_client import HttpClient as _DdgsHttpClient

logger = logging.getLogger(__name__)


def _probe_impersonate(browser: str) -> bool:
    """Return True if primp accepts *browser* without the noisy fallback warning."""
    buffer = io.StringIO()
    with contextlib.redirect_stderr(buffer):
        try:
            primp.Client(impersonate=browser)
        except Exception:
            return False
    return "does not exist" not in buffer.getvalue()


def _patch_ddgs_impersonates() -> None:
    """
    Best-effort shim for ddgs/primp mismatches.

    Some ddgs releases advertise browser impersonation strings that older primp
    builds do not recognise. When that happens primp emits noisy stderr warnings
    and may fall back unpredictably. We filter unsupported values once at import
    time so every DDGS() instance benefits.
    """
    candidates = getattr(_DdgsHttpClient, "_impersonates", None)
    if not candidates:
        logger.debug("ddgs HttpClient exposes no _impersonates; skipping primp shim")
        return

    supported = tuple(browser for browser in candidates if _probe_impersonate(browser))
    if not supported:
        logger.debug("ddgs/primp shim found no supported impersonate candidates")
        return

    if len(supported) < len(candidates):
        removed = sorted(set(candidates) - set(supported))
        logger.debug(
            "ddgs/primp mismatch detected; removed unsupported impersonates: %s",
            ", ".join(removed),
        )
        _DdgsHttpClient._impersonates = supported  # type: ignore[attr-defined,assignment]


_patch_ddgs_impersonates()


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
        self._cache: dict[str, tuple[float, list[dict]]] = {}

    def search_text(self, query: str, max_results: int | None = None) -> list[dict]:
        """Search DuckDuckGo for web results."""
        cache_key = f"text:{query}:{max_results or self._max_results}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._can_search():
            logger.warning("Search rate limit reached, returning empty results")
            return []

        results = self._search_ddg(
            "text",
            query,
            max_results=max_results or self._max_results,
        )
        self._set_cached(cache_key, results)
        return results

    def search_news(
        self,
        query: str,
        max_results: int | None = None,
        timelimit: str = "w",
    ) -> list[dict]:
        """Search DuckDuckGo for recent news articles."""
        cache_key = f"news:{query}:{max_results or self._max_results}:{timelimit}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._can_search():
            logger.warning("Search rate limit reached, returning empty results")
            return []

        results = self._search_ddg(
            "news",
            query,
            max_results=max_results or self._max_results,
            timelimit=timelimit,
        )
        self._set_cached(cache_key, results)
        return results

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
        queries_used: list[str] = []
        all_sources: list[dict] = []

        text_results = self.search_text(topic)
        queries_used.append(topic)

        if keywords:
            kw_query = f"{topic} {' '.join(keywords[:3])}"
            extra_results = self.search_text(kw_query, max_results=3)
            queries_used.append(kw_query)
            seen_urls = {result.get("href") for result in text_results}
            for result in extra_results:
                url = result.get("href")
                if url not in seen_urls:
                    text_results.append(result)
                    seen_urls.add(url)

        news_results: list[dict] = []
        if include_news:
            news_results = self.search_news(topic, max_results=3, timelimit="w")
            queries_used.append(f"news:{topic}")

        for result in text_results:
            all_sources.append(
                {
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                    "type": "web",
                }
            )

        for result in news_results:
            all_sources.append(
                {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("body", ""),
                    "type": "news",
                    "date": result.get("date"),
                    "source": result.get("source"),
                }
            )

        return {
            "text_results": text_results,
            "news_results": news_results,
            "sources": all_sources,
            "search_queries": queries_used,
        }

    def format_as_context(self, search_results: dict) -> str:
        """Format search results as a text block to inject into an LLM prompt."""
        parts: list[str] = []

        text_results = search_results.get("text_results", [])
        news_results = search_results.get("news_results", [])

        if text_results:
            parts.append("\n\n--- WEB RESEARCH RESULTS ---")
            parts.append(
                "Use the following recent web search results to inform your writing. "
                "Incorporate relevant facts, statistics, and insights. "
                "Cite sources where appropriate.\n"
            )
            for index, result in enumerate(text_results[:7], 1):
                title = result.get("title", "Untitled")
                url = result.get("href", "")
                body = self._clip_snippet(result.get("body", ""))
                parts.append(f"[{index}] {title}")
                parts.append(f"    URL: {url}")
                parts.append(f"    {body}\n")

        if news_results:
            parts.append("\n--- RECENT NEWS ---")
            for index, result in enumerate(news_results[:5], 1):
                title = result.get("title", "Untitled")
                url = result.get("url", "")
                body = self._clip_snippet(result.get("body", ""))
                date = result.get("date", "")
                source = result.get("source", "")
                parts.append(f"[News {index}] {title}")
                parts.append(f"    Source: {source} | Date: {date}")
                parts.append(f"    URL: {url}")
                parts.append(f"    {body}\n")

        if parts:
            parts.append("--- END OF RESEARCH ---\n")

        return "\n".join(parts)

    def reset(self):
        """Reset search count for a new generation request."""
        self._search_count = 0

    def _search_ddg(self, method_name: str, query: str, **kwargs) -> list[dict]:
        try:
            search_method = getattr(DDGS(), method_name)
            results = search_method(query=query, **kwargs)
            self._search_count += 1
            return list(results or [])
        except DDGSException as exc:
            message = str(exc)
            if "No results found" in message:
                logger.info("DuckDuckGo %s search for %r returned no results", method_name, query)
                return []
            logger.warning("DuckDuckGo %s search failed: %s", method_name, exc)
            return []
        except Exception as exc:
            logger.warning("DuckDuckGo %s search failed: %s", method_name, exc)
            return []

    @staticmethod
    def _clip_snippet(text: str, max_length: int = 240) -> str:
        cleaned = " ".join(str(text or "").split())
        if len(cleaned) <= max_length:
            return cleaned
        return cleaned[: max_length - 1].rstrip(" ,;:") + "…"

    def _can_search(self) -> bool:
        return self._search_count < self._max_searches

    def _get_cached(self, key: str) -> list[dict] | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        timestamp, results = entry
        if time.time() - timestamp > self._cache_ttl:
            del self._cache[key]
            return None
        return results

    def _set_cached(self, key: str, results: list[dict]):
        self._cache[key] = (time.time(), results)
