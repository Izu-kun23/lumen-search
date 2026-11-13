import time, json
from pathlib import Path
from app.domain.ranking import Index
from app.infrastructure.store import Store
from app.ops import digest, canonical


class SearchService:
    def __init__(self, store=None):
        self.store = store or Store()
        self.index = Index(self.store.documents())
        self.index_version = digest(canonical(self.store.documents()))

    def refresh(self):
        self.index = Index(self.store.documents())
        self.index_version = digest(canonical(self.store.documents()))

    def seed(self):
        for d in json.loads(
            (Path(__file__).parents[2] / "data/corpus.json").read_text()
        ):
            self.store.add(d["url"], d["title"], d["content"])
        self.refresh()

    def search(self, q, algorithm):
        start = time.perf_counter()
        results = self.index.search(q, algorithm)
        ms = (time.perf_counter() - start) * 1000
        self.store.log(q, len(results), ms)
        return {
            "index_version": self.index_version,
            "results": results,
            "count": len(results),
            "latency_ms": round(ms, 3),
            "algorithm": algorithm,
        }
