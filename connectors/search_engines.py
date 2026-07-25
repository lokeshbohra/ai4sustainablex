"""
ai4sustainablex — Search Engines Connector
Supports DuckDuckGo (free), Tavily (API key), and parallel multi-engine search.
"""

import os
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from duckduckgo_search import DDGS

from .base import BaseConnector, ConnectorConfig, ConnectorType


class SearchEngineConnector(BaseConnector):
    """
    Multi-engine search connector for ai4sustainablex.

    Supported search backends:
    - DuckDuckGo (free, no API key required — rate limited)
    - Tavily (requires API key — semantic search optimized)
    - Parallel search (runs both engines concurrently, deduplicates results)

    Configuration:
        api_key: Tavily API key (optional, for Tavily search)
        metadata.engines: List of engines to use ['duckduckgo', 'tavily']
    """

    def __init__(self, config: Optional[ConnectorConfig] = None):
        if config is None:
            config = ConnectorConfig(
                name="search_engines",
                connector_type=ConnectorType.SEARCH,
                api_key=os.getenv("TAVILY_API_KEY"),
                metadata={
                    "engines": ["duckduckgo", "tavily"],
                    "max_results_per_engine": 10,
                },
            )
        super().__init__(config)
        self._tavily_key = self.config.api_key
        self._engines = self.config.metadata.get("engines", ["duckduckgo"])
        self._max_results = self.config.metadata.get("max_results_per_engine", 10)
        self._ddgs: Optional[DDGS] = None

    @property
    def ddgs(self):
        """Lazy-init DuckDuckGo search client."""
        if self._ddgs is None:
            self._ddgs = DDGS()
        return self._ddgs

    def authenticate(self) -> bool:
        """
        Validate search engine configuration.
        DuckDuckGo is always available (no auth needed).
        Tavily requires a valid API key.
        """
        if "tavily" not in self._engines:
            self._authenticated = True
            return True

        if not self._tavily_key:
            self._authenticated = False
            return False

        try:
            resp = requests.post(
                "https://api.tavily.com/search",
                json={"api_key": self._tavily_key, "query": "test", "max_results": 1},
                timeout=10,
            )
            self._authenticated = resp.status_code == 200
        except requests.RequestException:
            self._authenticated = False
        return self._authenticated

    def fetch(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generic fetch not used by search engines. Use search() instead."""
        return {"error": "Use search() method for search engines", "data": {}}

    def search(self, query: str, top_k: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """
        Search across configured engines.

        Args:
            query: The search query
            top_k: Number of results to return
            **kwargs:
                parallel: If True, run all engines concurrently
                engines: Override configured engines list
                deduplicate: If True, remove duplicate URLs

        Returns:
            List of result dicts: {title, url, snippet, source}
        """
        parallel = kwargs.get("parallel", True)
        engines = kwargs.get("engines", self._engines)
        deduplicate = kwargs.get("deduplicate", True)

        if parallel and len(engines) > 1:
            return self._parallel_search(query, top_k, engines, deduplicate)
        else:
            return self._sequential_search(query, top_k, engines, deduplicate)

    def _sequential_search(self, query: str, top_k: int,
                           engines: List[str], deduplicate: bool) -> List[Dict[str, Any]]:
        """Search engines sequentially, collecting results."""
        all_results = []
        seen_urls = set()

        for engine in engines:
            per_engine = max(1, top_k // len(engines))
            if engine == "duckduckgo":
                results = self._search_duckduckgo(query, per_engine)
            elif engine == "tavily":
                results = self._search_tavily(query, per_engine)
            else:
                continue

            for r in results:
                url = r.get("url", "")
                if deduplicate and url in seen_urls:
                    continue
                seen_urls.add(url)
                all_results.append(r)

        return all_results[:top_k]

    def _parallel_search(self, query: str, top_k: int,
                         engines: List[str], deduplicate: bool) -> List[Dict[str, Any]]:
        """Search all engines concurrently using thread pool."""
        all_results = []
        seen_urls = set()
        per_engine = max(1, top_k // len(engines))

        with ThreadPoolExecutor(max_workers=len(engines)) as executor:
            futures = {}
            for engine in engines:
                if engine == "duckduckgo":
                    future = executor.submit(self._search_duckduckgo, query, per_engine)
                elif engine == "tavily":
                    future = executor.submit(self._search_tavily, query, per_engine)
                else:
                    continue
                futures[future] = engine

            for future in as_completed(futures):
                engine = futures[future]
                try:
                    results = future.result(timeout=15)
                    for r in results:
                        url = r.get("url", "")
                        if deduplicate and url in seen_urls:
                            continue
                        seen_urls.add(url)
                        all_results.append(r)
                except Exception as e:
                    print(f"⚠️ {engine} search failed: {e}")

        return all_results[:top_k]

    def _search_duckduckgo(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo (free, no API key needed)."""
        results = []
        try:
            ddg_results = list(self.ddgs.text(
                query,
                max_results=min(max_results, 20),
                safesearch="moderate",
            ))
            for r in ddg_results:
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                    "source": "duckduckgo",
                })
        except Exception as e:
            print(f"⚠️ DuckDuckGo search error: {e}")
        return results

    def _search_tavily(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search using Tavily API (requires API key)."""
        results = []
        if not self._tavily_key:
            return results
        try:
            resp = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self._tavily_key,
                    "query": query,
                    "max_results": max_results,
                    "search_depth": "advanced",
                    "include_answer": True,
                },
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                for r in data.get("results", []):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "snippet": r.get("content", ""),
                        "source": "tavily",
                        "score": r.get("score", 0),
                    })
        except Exception as e:
            print(f"⚠️ Tavily search error: {e}")
        return results

    def web_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Web search convenience method using DuckDuckGo.
        Used for supplementary research during report generation.
        """
        return self._search_duckduckgo(query, max_results)

    def health_check(self) -> bool:
        """Check if at least one search engine is available."""
        try:
            test_results = self._search_duckduckgo("sustainability ESG reporting", 1)
            return len(test_results) > 0
        except Exception:
            return False

    def validate_key(self) -> Dict[str, Any]:
        """Return search engine configuration status."""
        duck_available = True
        try:
            test = self._search_duckduckgo("test", 1)
            duck_available = len(test) > 0
        except Exception:
            duck_available = False

        tavily_available = bool(self._tavily_key) and self._authenticated

        return {
            "valid": duck_available or tavily_available,
            "message": self._get_status_message(duck_available, tavily_available),
            "tier": "premium" if tavily_available else "free",
            "engines": {
                "duckduckgo": {"available": duck_available, "config": "No API key required"},
                "tavily": {
                    "available": tavily_available,
                    "config": "API key configured" if self._tavily_key else "No API key",
                },
            },
        }

    @staticmethod
    def _get_status_message(duck: bool, tavily: bool) -> str:
        if duck and tavily:
            return "DuckDuckGo + Tavily both operational"
        elif duck:
            return "DuckDuckGo operational (Tavily not configured)"
        elif tavily:
            return "Tavily operational (DuckDuckGo unavailable)"
        return "No search engines available"