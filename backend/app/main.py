import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.v1.endpoints import router as api_v1_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Multi-Agent AI Research Platform Backend powered by LangGraph & FastAPI",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API v{settings.VERSION}",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }


@app.get("/api/v1/download-sample/{filename}")
async def download_sample(filename: str):
    allowed_files = [
        "Universal_Basic_Income_Research_2025.txt",
        "Universal_Basic_Income_Research_2025.pdf",
        "Universal_Basic_Income_Research_2025.md",
        "Quantum_Grid_Optimization_Whitepaper_2025.pdf"
    ]
    if filename not in allowed_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = os.path.join(r"D:\Projects-Personal\researchmind-ai", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File does not exist")
    
    return FileResponse(path=file_path, filename=filename, media_type="application/octet-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
