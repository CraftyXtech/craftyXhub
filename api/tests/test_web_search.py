"""
Tests for WebSearchService — DuckDuckGo integration.
"""

import time
from unittest.mock import patch, MagicMock
import pytest
from services.ai.web_search import WebSearchService


MOCK_TEXT_RESULTS = [
    {
        "title": "AI Trends 2026 - TechCrunch",
        "href": "https://techcrunch.com/ai-trends-2026",
        "body": "The latest AI trends shaping 2026 include...",
    },
    {
        "title": "Machine Learning Advances",
        "href": "https://example.com/ml-advances",
        "body": "Recent advances in machine learning have...",
    },
]

MOCK_NEWS_RESULTS = [
    {
        "date": "2026-02-25T10:00:00+00:00",
        "title": "OpenAI Announces New Model",
        "body": "OpenAI has released a new flagship model...",
        "url": "https://news.example.com/openai",
        "image": "https://img.example.com/thumb.jpg",
        "source": "TechNews",
    },
]


class TestWebSearchServiceTextSearch:
    """Tests for text search functionality."""

    @patch("services.ai.web_search.DDGS")
    def test_search_text_returns_results(self, mock_ddgs):
        mock_instance = MagicMock()
        mock_instance.text.return_value = MOCK_TEXT_RESULTS
        mock_ddgs.return_value = mock_instance

        svc = WebSearchService(max_results=5)
        results = svc.search_text("AI trends 2026")

        assert len(results) == 2
        assert results[0]["title"] == "AI Trends 2026 - TechCrunch"
        assert "href" in results[0]
        mock_instance.text.assert_called_once_with("AI trends 2026", max_results=5)

    @patch("services.ai.web_search.DDGS")
    def test_search_text_returns_empty_on_failure(self, mock_ddgs):
        mock_instance = MagicMock()
        mock_instance.text.side_effect = Exception("Network error")
        mock_ddgs.return_value = mock_instance

        svc = WebSearchService()
        results = svc.search_text("test query")

        assert results == []


class TestWebSearchServiceNewsSearch:
    """Tests for news search functionality."""

    @patch("services.ai.web_search.DDGS")
    def test_search_news_returns_results(self, mock_ddgs):
        mock_instance = MagicMock()
        mock_instance.news.return_value = MOCK_NEWS_RESULTS
        mock_ddgs.return_value = mock_instance

        svc = WebSearchService(max_results=3)
        results = svc.search_news("AI news", timelimit="w")

        assert len(results) == 1
        assert results[0]["source"] == "TechNews"
        mock_instance.news.assert_called_once_with(
            "AI news", max_results=3, timelimit="w"
        )


class TestWebSearchServiceTopicSearch:
    """Tests for combined topic search."""

    @patch("services.ai.web_search.DDGS")
    def test_search_for_topic_combines_results(self, mock_ddgs):
        mock_instance = MagicMock()
        mock_instance.text.return_value = MOCK_TEXT_RESULTS
        mock_instance.news.return_value = MOCK_NEWS_RESULTS
        mock_ddgs.return_value = mock_instance

        svc = WebSearchService(max_results=5)
        results = svc.search_for_topic("AI trends", keywords=["machine learning"])

        assert "text_results" in results
        assert "news_results" in results
        assert "sources" in results
        assert len(results["sources"]) > 0
        # Text + news sources
        web_sources = [s for s in results["sources"] if s["type"] == "web"]
        news_sources = [s for s in results["sources"] if s["type"] == "news"]
        assert len(web_sources) > 0
        assert len(news_sources) > 0


class TestWebSearchServiceCache:
    """Tests for caching behaviour."""

    @patch("services.ai.web_search.DDGS")
    def test_cache_prevents_duplicate_searches(self, mock_ddgs):
        mock_instance = MagicMock()
        mock_instance.text.return_value = MOCK_TEXT_RESULTS
        mock_ddgs.return_value = mock_instance

        svc = WebSearchService(max_results=5)

        # First call — hits DuckDuckGo
        r1 = svc.search_text("cached query")
        # Second call — should hit cache
        r2 = svc.search_text("cached query")

        assert r1 == r2
        # DDGS().text() should only be called once
        assert mock_instance.text.call_count == 1

    @patch("services.ai.web_search.DDGS")
    def test_cache_expires_after_ttl(self, mock_ddgs):
        mock_instance = MagicMock()
        mock_instance.text.return_value = MOCK_TEXT_RESULTS
        mock_ddgs.return_value = mock_instance

        svc = WebSearchService(max_results=5, cache_ttl=0)  # Instant expiry

        svc.search_text("expiring query")
        time.sleep(0.01)
        svc.search_text("expiring query")

        assert mock_instance.text.call_count == 2


class TestWebSearchServiceRateLimit:
    """Tests for rate limiting."""

    @patch("services.ai.web_search.DDGS")
    def test_rate_limit_stops_searches(self, mock_ddgs):
        mock_instance = MagicMock()
        mock_instance.text.return_value = MOCK_TEXT_RESULTS
        mock_ddgs.return_value = mock_instance

        svc = WebSearchService(max_searches_per_request=2)

        svc.search_text("q1")
        svc.search_text("q2")
        # Third search should be blocked
        r3 = svc.search_text("q3")

        assert r3 == []
        assert mock_instance.text.call_count == 2

    @patch("services.ai.web_search.DDGS")
    def test_reset_clears_rate_limit(self, mock_ddgs):
        mock_instance = MagicMock()
        mock_instance.text.return_value = MOCK_TEXT_RESULTS
        mock_ddgs.return_value = mock_instance

        svc = WebSearchService(max_searches_per_request=1)
        svc.search_text("q1")
        r2 = svc.search_text("q2")
        assert r2 == []

        svc.reset()
        r3 = svc.search_text("q3")
        assert len(r3) == 2  # Back to working


class TestWebSearchServiceFormatContext:
    """Tests for prompt context formatting."""

    def test_format_as_context_with_results(self):
        svc = WebSearchService()
        search_results = {
            "text_results": MOCK_TEXT_RESULTS,
            "news_results": MOCK_NEWS_RESULTS,
        }

        context = svc.format_as_context(search_results)

        assert "WEB RESEARCH RESULTS" in context
        assert "RECENT NEWS" in context
        assert "AI Trends 2026 - TechCrunch" in context
        assert "OpenAI Announces New Model" in context
        assert "END OF RESEARCH" in context

    def test_format_as_context_empty_results(self):
        svc = WebSearchService()
        context = svc.format_as_context({"text_results": [], "news_results": []})

        assert context == ""
