import re

import httpx
from loguru import logger

from app.schemas.source import PaperItem

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
    "to", "was", "were", "will", "with", "we", "this", "these", "those",
    "or", "can", "our", "their", "into", "across", "been", "through",
    "between", "difference", "different", "versus", "vs", "study", "using",
}


class SemanticScholarService:
    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

    def search_papers(self, query: str, limit: int = 5) -> list[PaperItem]:
        logger.info(f"Searching Semantic Scholar papers for query: '{query}'")
        params = {
            "query": query,
            "limit": max(limit * 2, 6),
            "fields": "title,authors,year,abstract,url,citationCount,venue",
        }

        query_keywords = {
            w for w in re.findall(r"\b[a-zA-Z]{3,}\b", query.lower())
            if w not in STOPWORDS
        }

        try:
            with httpx.Client(timeout=4.0) as client:
                resp = client.get(self.BASE_URL, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    papers = []
                    for item in data.get("data", []):
                        title = item.get("title", "Untitled")
                        abstract = item.get("abstract") or ""

                        # Relevance check: if query has keywords, ensure at least one matches
                        if query_keywords:
                            combined = f"{title} {abstract}".lower()
                            if not any(kw in combined for kw in query_keywords):
                                continue

                        authors = [a.get("name", "") for a in item.get("authors", []) if a.get("name")]
                        papers.append(
                            PaperItem(
                                id=f"s2_{item.get('paperId', 'unknown')}",
                                title=title,
                                authors=authors,
                                published_year=item.get("year"),
                                abstract=abstract or "Abstract unavailable",
                                url=item.get("url") or f"https://www.semanticscholar.org/search?q={query}",
                                citation_count=item.get("citationCount", 0),
                                venue=item.get("venue") or "Semantic Scholar",
                            )
                        )
                    return papers[:limit]
                else:
                    logger.warning(f"Semantic Scholar API status code: {resp.status_code}")
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Semantic Scholar API request failed: {e}")

        # In production, never fabricate mock papers if the external API is unreachable or returns 429
        return []
