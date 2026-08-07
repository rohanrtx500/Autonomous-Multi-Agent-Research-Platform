import os
from typing import List, Dict, Any, Optional
from loguru import logger
from app.schemas.source import SourceDocument

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import docx
except ImportError:
    docx = None

try:
    import pptx
except ImportError:
    pptx = None


class DocumentLoaderService:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_file(self, file_path: str, filename: Optional[str] = None) -> List[SourceDocument]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at path: {file_path}")

        name = filename or os.path.basename(file_path)
        ext = os.path.splitext(name)[1].lower()

        logger.info(f"Loading document: {name} (extension: {ext})")
        text_content = ""

        if ext in [".txt", ".md", ".csv", ".html"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text_content = f.read()

        elif ext == ".pdf":
            if pypdf:
                reader = pypdf.PdfReader(file_path)
                pages = [page.extract_text() or "" for page in reader.pages]
                text_content = "\n\n".join(pages)
            else:
                logger.warning("pypdf not installed, reading text fallback")
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text_content = f.read()

        elif ext == ".docx":
            if docx:
                doc = docx.Document(file_path)
                text_content = "\n".join([p.text for p in doc.paragraphs if p.text])
            else:
                text_content = f"Docx content fallback for {name}"

        elif ext == ".pptx":
            if pptx:
                prs = pptx.Presentation(file_path)
                slides_text = []
                for slide in prs.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text") and shape.text:
                            slides_text.append(shape.text)
                text_content = "\n".join(slides_text)
            else:
                text_content = f"PPTX content fallback for {name}"
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text_content = f.read()

        chunks = self.chunk_text(text_content)
        documents = []
        for idx, chunk in enumerate(chunks):
            doc_id = f"{name}_chunk_{idx}"
            documents.append(
                SourceDocument(
                    id=doc_id,
                    title=f"{name} (Part {idx + 1})",
                    content=chunk,
                    source_type="user_doc",
                    url=file_path,
                    metadata={"file_name": name, "chunk_index": idx, "total_chunks": len(chunks)}
                )
            )
        return documents

    def chunk_text(self, text: str) -> List[str]:
        if not text:
            return []
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size
            if end >= text_length:
                chunks.append(text[start:])
                break
            # try to split on paragraph or sentence boundary
            last_newline = text.rfind("\n", start, end)
            if last_newline != -1 and last_newline > start + (self.chunk_size // 2):
                end = last_newline
            chunks.append(text[start:end].strip())
            start = end - self.chunk_overlap
            if start < 0 or start >= text_length:
                break
        return [c for c in chunks if c]
