from typing import Any, Literal

from pydantic import BaseModel, Field


class SourceDocument(BaseModel):
    id: str
    title: str
    content: str
    source_type: Literal["arxiv", "semantic_scholar", "web", "github", "user_doc"]
    url: str | None = None
    author: str | None = None
    published_date: str | None = None
    score: float = 1.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class PaperItem(BaseModel):
    id: str
    title: str
    authors: list[str] = Field(default_factory=list)
    published_year: int | None = None
    abstract: str
    url: str
    pdf_url: str | None = None
    citation_count: int = 0
    venue: str | None = None


class GitHubRepoItem(BaseModel):
    name: str
    full_name: str
    description: str | None = None
    url: str
    stars: int = 0
    language: str | None = None
    topics: list[str] = Field(default_factory=list)
    readme_snippet: str | None = None
