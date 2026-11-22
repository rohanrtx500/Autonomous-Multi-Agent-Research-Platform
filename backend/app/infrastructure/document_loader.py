import os

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
    def __init__(self, chunk_size: int = 2500, chunk_overlap: int = 200, max_chunks: int = 30):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_chunks = max_chunks

    def load_file(self, file_path: str, filename: str | None = None) -> list[SourceDocument]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at path: {file_path}")

        name = filename or os.path.basename(file_path)
        ext = os.path.splitext(name)[1].lower()

        logger.info(f"Extracting document text: {name} (type: {ext})")
        text_content = ""

        if ext in [".txt", ".md", ".csv", ".html"]:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text_content = f.read()
            except UnicodeDecodeError:
                # Fallback with error replacement for non-standard encodings
                with open(file_path, "r", encoding="latin-1", errors="replace") as f:
                    text_content = f.read()

        elif ext == ".pdf":
            if not pypdf:
                raise RuntimeError("pypdf is not installed. PDF parsing unavailable.")
            try:
                reader = pypdf.PdfReader(file_path)
                pages = []
                for p_idx, page in enumerate(reader.pages):
                    p_text = page.extract_text() or ""
                    if p_text.strip():
                        pages.append(p_text.strip())
                if not pages:
                    raise ValueError(f"PDF document {name} contains no extractable text (may be image-only scan or encrypted).")
                text_content = "\n\n".join(pages)
            except Exception as e:
                logger.error(f"Failed to extract text from PDF {name}: {e}")
                raise ValueError(f"Corrupted or unreadable PDF: {e}") from e

        elif ext == ".docx":
            if not docx:
                raise RuntimeError("python-docx is not installed. DOCX parsing unavailable.")
            try:
                doc = docx.Document(file_path)
                paras = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
                # Also extract text from tables
                for table in doc.tables:
                    for row in table.rows:
                        row_texts = [c.text.strip() for c in row.cells if c.text and c.text.strip()]
                        if row_texts:
                            paras.append(" | ".join(row_texts))
                if not paras:
                    raise ValueError(f"DOCX document {name} is empty or contains no extractable text.")
                text_content = "\n\n".join(paras)
            except Exception as e:
                logger.error(f"Failed to extract text from DOCX {name}: {e}")
                raise ValueError(f"Corrupted or unreadable DOCX: {e}") from e

        elif ext == ".pptx":
            if not pptx:
                raise RuntimeError("python-pptx is not installed. PPTX parsing unavailable.")
            try:
                prs = pptx.Presentation(file_path)
                slides_text = []
                for s_idx, slide in enumerate(prs.slides):
                    for shape in slide.shapes:
                        if hasattr(shape, "text") and shape.text and shape.text.strip():
                            slides_text.append(shape.text.strip())
                if not slides_text:
                    raise ValueError(f"PPTX presentation {name} contains no extractable text.")
                text_content = "\n\n".join(slides_text)
            except Exception as e:
                logger.error(f"Failed to extract text from PPTX {name}: {e}")
                raise ValueError(f"Corrupted or unreadable PPTX: {e}") from e

        else:
            raise ValueError(f"Unsupported document format '{ext}'. Allowed: .pdf, .docx, .pptx, .txt, .md, .csv, .html")

        if not text_content or len(text_content.strip()) < 10:
            raise ValueError(f"Extracted document text from {name} is insufficient or empty.")

        chunks = self.chunk_text(text_content)
        total_extracted = len(chunks)

        # Smart Stratified Sampling if chunks exceed max_chunks (protects free-tier memory and timeouts)
        if len(chunks) > self.max_chunks:
            logger.info(f"Document {name} generated {len(chunks)} chunks, stratifying to top {self.max_chunks} key chunks.")
            front_k = self.max_chunks // 3
            back_k = self.max_chunks // 3
            mid_k = self.max_chunks - front_k - back_k

            front_chunks = chunks[:front_k]
            back_chunks = chunks[-back_k:] if back_k > 0 else []
            mid_candidates = chunks[front_k:-back_k] if back_k > 0 else chunks[front_k:]

            if mid_candidates and mid_k > 0:
                step = max(1, len(mid_candidates) // mid_k)
                mid_chunks = [mid_candidates[i] for i in range(0, len(mid_candidates), step)][:mid_k]
            else:
                mid_chunks = []

            chunks = front_chunks + mid_chunks + back_chunks

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
                    metadata={
                        "file_name": name,
                        "chunk_index": idx,
                        "total_chunks": len(chunks),
                        "extracted_chunks": total_extracted,
                        "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    }
                )
            )
        logger.info(f"Successfully processed {name}: generated {len(documents)} text chunks.")
        return documents

    def chunk_text(self, text: str) -> list[str]:
        if not text:
            return []
        chunks = []
        start = 0
        text_length = len(text)
        min_advance = max(1, self.chunk_size - self.chunk_overlap)

        while start < text_length:
            end = start + self.chunk_size
            if end >= text_length:
                chunk = text[start:].strip()
                if chunk:
                    chunks.append(chunk)
                break

            # Search for natural boundary in the latter 50% of the window
            search_start = start + (self.chunk_size // 2)
            break_point = text.rfind("\n\n", search_start, end)
            if break_point == -1:
                break_point = text.rfind(". ", search_start, end)
                if break_point != -1:
                    break_point += 1
            if break_point == -1:
                break_point = end

            chunk = text[start:break_point].strip()
            if chunk:
                chunks.append(chunk)

            # Guaranteed healthy forward progress
            next_start = break_point - self.chunk_overlap
            if next_start <= start:
                next_start = start + min_advance
            start = next_start

        return chunks
