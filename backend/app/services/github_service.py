from typing import List
import httpx
from loguru import logger
from app.core.config import settings
from app.schemas.source import GitHubRepoItem


class GitHubSearchService:
    BASE_URL = "https://api.github.com/search/repositories"

    def __init__(self):
        self.token = settings.GITHUB_TOKEN

    def search_repositories(self, query: str, max_results: int = 5) -> List[GitHubRepoItem]:
        logger.info(f"Searching GitHub repositories for query: '{query}'")
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ResearchMind-AI-Agent"
        }
        if self.token and "your_" not in self.token:
            headers["Authorization"] = f"token {self.token}"

        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": max_results,
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(self.BASE_URL, headers=headers, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    repos = []
                    for item in data.get("items", []):
                        repos.append(
                            GitHubRepoItem(
                                name=item.get("name", ""),
                                full_name=item.get("full_name", ""),
                                description=item.get("description") or "Open-source codebase implementation.",
                                url=item.get("html_url", ""),
                                stars=item.get("stargazers_count", 0),
                                language=item.get("language") or "Python",
                                topics=item.get("topics", []),
                                readme_snippet=f"Repository implementation for {query} with {item.get('stargazers_count', 0)} stars.",
                            )
                        )
                    # For non-code/non-technical queries that return no items or low-relevance items, return what was found or empty
                    return repos
                else:
                    logger.warning(f"GitHub API status code: {resp.status_code}")
        except Exception as e:
            logger.error(f"Error querying GitHub API: {e}")

        # Return empty list if query is non-technical or API search returned no items
        return []
