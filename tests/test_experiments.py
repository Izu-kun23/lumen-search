from app.experiments import run
from app.infrastructure.store import Store
from app.services.search import SearchService


def test_release_retrieval_gates(tmp_path):
    record, path = run(tmp_path / "runs")
    assert record["passed"] and path.exists()
    assert record["metrics"]["bm25"]["mrr"] >= 0.75


def test_index_version_changes_after_document_update(tmp_path):
    store = Store(str(tmp_path / "search.db"))
    store.add("https://example.org", "Before", "index information")
    service = SearchService(store)
    before = service.index_version
    store.add("https://example.org", "After", "new ranking evidence")
    service.refresh()
    assert before != service.index_version
    assert service.search("ranking", "bm25")["index_version"] == service.index_version
