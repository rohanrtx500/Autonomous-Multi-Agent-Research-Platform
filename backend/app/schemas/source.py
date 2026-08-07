from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SourceDocument(BaseModel):
    id: str
    title: str
    content: str
    source_type: Literal["arxiv", "semantic_scholar", "web", "github", "user_doc"]
    url: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[str] = None
    score: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PaperItem(BaseModel):
    id: str
    title: str
    authors: List[str] = Field(default_factory=list)
    published_year: Optional[int] = None
    abstract: str
    url: str
    pdf_url: Optional[str] = None
    citation_count: int = 0
    venue: Optional[str] = None


class GitHubRepoItem(BaseModel):
    name: str
    full_name: str
    description: Optional[str] = None
    url: str
    stars: int = 0
    language: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    readme_snippet: Optional[str] = None
