TITLE = "Lumen Search"

from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

WEB = Path(__file__).parent / "web"
app = FastAPI(title=TITLE, version="1.0.0")
app.mount("/assets", StaticFiles(directory=WEB), name="assets")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(WEB / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "project": TITLE}


from typing import Literal
from pydantic import BaseModel, Field
from fastapi import HTTPException, Query
from app.services.search import SearchService
from app.services.crawler import crawl

service = SearchService()
if not service.store.documents():
    service.seed()


class CrawlRequest(BaseModel):
    url: str = Field(max_length=2048)
    max_pages: int = Field(default=5, ge=1, le=10)


@app.get("/api/search")
def search(
    q: str = Query(min_length=1, max_length=300),
    algorithm: Literal["bm25", "tfidf"] = "bm25",
):
    return service.search(q, algorithm)


@app.get("/api/suggest")
def suggest(q: str = Query(default="", max_length=100)):
    return service.index.suggest(q)


@app.get("/api/stats")
def stats():
    return {
        "documents": len(service.index.documents),
        "terms": len(service.index.postings),
        **service.store.analytics(),
    }


@app.post("/api/crawl")
def crawl_url(body: CrawlRequest):
    try:
        result = crawl(body.url, service.store, body.max_pages)
        service.refresh()
        return result
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc
