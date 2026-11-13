import pytest
from app.domain.ranking import Index
from app.infrastructure.store import Store
from app.services.search import SearchService


def fixture():
    return Index(
        [
            {"id": 1, "title": "A", "content": "machine learning improves search"},
            {"id": 2, "title": "B", "content": "learning machine order matters"},
            {"id": 3, "title": "C", "content": "rareterm rareterm"},
        ]
    )


def test_phrase_order():
    i = fixture()
    assert [r["id"] for r in i.search('"machine learning"')] == [1]
    assert [r["id"] for r in i.search('"learning machine"')] == [2]


def test_ranking_and_empty():
    for a in ["bm25", "tfidf"]:
        assert fixture().search("rareterm", a)[0]["id"] == 3
        assert fixture().search("unfindable", a) == []


def test_persistence_and_analytics(tmp_path):
    store = Store(str(tmp_path / "test.db"))
    store.add("https://example.org", "Test", "search ranking")
    store.add("https://example.org", "Updated", "search ranking")
    s = SearchService(store)
    assert len(store.documents()) == 1
    assert s.search("ranking", "bm25")["count"] == 1
    assert store.analytics()["queries"] == 1


def test_ssrf_deny_by_default(monkeypatch):
    from app.services.crawler import validate_url

    monkeypatch.setenv("CRAWL_ALLOWED_HOSTS", "")
    with pytest.raises(ValueError):
        validate_url("http://127.0.0.1")


def test_private_allowlist_still_blocked(monkeypatch):
    from app.services.crawler import validate_url

    monkeypatch.setenv("CRAWL_ALLOWED_HOSTS", "127.0.0.1")
    with pytest.raises(ValueError):
        validate_url("http://127.0.0.1")


def test_api():
    from fastapi.testclient import TestClient
    from app.main import app

    c = TestClient(app)
    assert c.get("/").status_code == 200
    assert c.get("/api/search?q=bm25").json()["count"] > 0
    assert c.get("/api/search?q=x&algorithm=bad").status_code == 422
