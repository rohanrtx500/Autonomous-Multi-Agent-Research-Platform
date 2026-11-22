import re
import xml.etree.ElementTree as ET

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


class ArxivService:
    BASE_URL = "https://export.arxiv.org/api/query"

    def search_papers(self, query: str, max_results: int = 5) -> list[PaperItem]:
        logger.info(f"Searching arXiv papers for query: '{query}'")
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max(max_results * 2, 6),
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        try:
            with httpx.Client(timeout=4.0) as client:
                resp = client.get(self.BASE_URL, params=params)
                if resp.status_code == 200:
                    parsed = self._parse_atom_feed(resp.text, query=query)
                    return parsed[:max_results]
                else:
                    logger.warning(f"arXiv API returned status code: {resp.status_code}")
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Error querying arXiv API: {e}")

        return []

    def _parse_atom_feed(self, xml_text: str, query: str = "") -> list[PaperItem]:
        papers = []
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }

        # Extract significant query keywords to filter out completely irrelevant preprints
        query_keywords = {
            w for w in re.findall(r"\b[a-zA-Z]{3,}\b", query.lower())
            if w not in STOPWORDS
        }

        try:
            root = ET.fromstring(xml_text)
            entries = root.findall("atom:entry", ns)
            for entry in entries:
                id_elem = entry.find("atom:id", ns)
                title_elem = entry.find("atom:title", ns)
                summary_elem = entry.find("atom:summary", ns)
                published_elem = entry.find("atom:published", ns)

                paper_id = id_elem.text.split("/abs/")[-1] if id_elem is not None and id_elem.text else "arxiv_doc"
                title = title_elem.text.strip().replace("\n", " ") if title_elem is not None and title_elem.text else "Untitled Paper"
                abstract = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None and summary_elem.text else ""

                # Relevance check: if query has significant keywords, ensure at least one is present in title or abstract
                if query_keywords:
                    combined_text = f"{title} {abstract}".lower()
                    if not any(kw in combined_text for kw in query_keywords):
                        continue

                year = None
                if published_elem is not None and published_elem.text:
                    year = int(published_elem.text[:4])

                authors = []
                for author_node in entry.findall("atom:author", ns):
                    name_node = author_node.find("atom:name", ns)
                    if name_node is not None and name_node.text:
                        authors.append(name_node.text)

                pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
                abs_url = f"https://arxiv.org/abs/{paper_id}"

                papers.append(
                    PaperItem(
                        id=f"arxiv_{paper_id}",
                        title=title,
                        authors=authors,
                        published_year=year,
                        abstract=abstract,
                        url=abs_url,
                        pdf_url=pdf_url,
                        venue="arXiv",
                    )
                )
        except Exception as e:  # noqa: BLE001
            logger.error(f"Error parsing arXiv XML feed: {e}")

        return papers
