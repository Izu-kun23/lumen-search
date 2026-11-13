"""Fixed-corpus retrieval gates and versioned experiment records."""

import argparse, json
from app.ops import ROOT, file_digest, save_run
from app.domain.ranking import Index


def run(output):
    path = ROOT / "data/corpus.json"
    documents = [
        dict(id=str(i + 1), **d) for i, d in enumerate(json.loads(path.read_text()))
    ]
    index = Index(documents)
    judgments = {
        "bm25 ranking": {"2", "12"},
        "web crawler": {"3"},
        "fraud detection": {"8"},
        "phrase queries": {"11"},
        "database indexes": {"6"},
        "retrieval augmented generation": {"5"},
    }
    metrics = {}
    for algorithm in ["bm25", "tfidf"]:
        rr = []
        recall = []
        for query, relevant in judgments.items():
            ids = [str(d["id"]) for d in index.search(query, algorithm)[:5]]
            rr.append(
                next((1 / (i + 1) for i, id in enumerate(ids) if id in relevant), 0)
            )
            recall.append(len(set(ids) & relevant) / len(relevant))
        metrics[algorithm] = {
            "mrr": sum(rr) / len(rr),
            "recall_at_5": sum(recall) / len(recall),
        }
    gates = {
        "unique_urls": len({d["url"] for d in documents}) == len(documents),
        "nonempty_content": all(d["content"].strip() for d in documents),
        "bm25_mrr_at_least_075": metrics["bm25"]["mrr"] >= 0.75,
        "tfidf_mrr_at_least_075": metrics["tfidf"]["mrr"] >= 0.75,
        "phrase_order": bool(index.search('"inverted index"'))
        and not index.search('"index inverted"'),
    }
    config = {
        "corpus_sha256": file_digest(path),
        "judgments": {q: sorted(ids) for q, ids in judgments.items()},
        "algorithms": ["bm25", "tfidf"],
        "scope": "small fixed-corpus functional benchmark",
    }
    return save_run(output, config, metrics, gates)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="artifacts/runs")
    args = p.parse_args()
    record, path = run(args.output)
    print(
        json.dumps(
            {
                "record": str(path),
                "passed": record["passed"],
                "metrics": record["metrics"],
            },
            indent=2,
        )
    )
    raise SystemExit(0 if record["passed"] else 1)


if __name__ == "__main__":
    main()
