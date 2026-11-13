import sqlite3, os, json
from pathlib import Path


class Store:
    def __init__(self, path=None):
        self.path = path or os.getenv("SEARCH_DB", "data/search.db")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY,url TEXT UNIQUE,title TEXT,content TEXT)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS queries(id INTEGER PRIMARY KEY,query TEXT,count INTEGER,latency REAL,created TEXT DEFAULT CURRENT_TIMESTAMP)"
            )

    def connect(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        return db

    def add(self, url, title, content):
        with self.connect() as db:
            db.execute(
                "INSERT INTO documents(url,title,content) VALUES(?,?,?) ON CONFLICT(url) DO UPDATE SET title=excluded.title,content=excluded.content",
                (url, title, content),
            )

    def documents(self):
        with self.connect() as db:
            return [dict(x) for x in db.execute("SELECT * FROM documents ORDER BY id")]

    def log(self, q, count, latency):
        with self.connect() as db:
            db.execute(
                "INSERT INTO queries(query,count,latency) VALUES(?,?,?)",
                (q, count, latency),
            )

    def analytics(self):
        with self.connect() as db:
            return {
                "queries": db.execute("SELECT count(*) FROM queries").fetchone()[0],
                "average_latency_ms": round(
                    db.execute(
                        "SELECT coalesce(avg(latency),0) FROM queries"
                    ).fetchone()[0],
                    2,
                ),
                "popular": [
                    dict(x)
                    for x in db.execute(
                        "SELECT query,count(*) AS searches FROM queries GROUP BY query ORDER BY searches DESC LIMIT 5"
                    )
                ],
            }
