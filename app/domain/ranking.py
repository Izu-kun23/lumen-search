"""Position-aware inverted index and Okapi BM25; no search-engine dependency."""

import math, re
from collections import Counter, defaultdict


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


class Index:
    def __init__(self, documents):
        self.documents = {str(d["id"]): d for d in documents}
        self.postings = defaultdict(dict)
        self.lengths = {}
        for key, doc in self.documents.items():
            tokens = tokenize(doc["title"] + " " + doc["content"])
            self.lengths[key] = len(tokens)
            positions = defaultdict(list)
            for i, t in enumerate(tokens):
                positions[t].append(i)
            for t, p in positions.items():
                self.postings[t][key] = p
        self.average = sum(self.lengths.values()) / max(len(documents), 1)

    def search(self, query, algorithm="bm25", limit=20):
        terms = tokenize(query)
        scores = defaultdict(float)
        n = len(self.documents)
        phrases = [tokenize(p) for p in re.findall(r'"([^"]+)"', query)]
        for term in terms:
            posting = self.postings.get(term, {})
            for key, positions in posting.items():
                tf = len(positions)
                df = len(posting)
                if algorithm == "tfidf":
                    scores[key] += (1 + math.log(tf)) * math.log(1 + n / (1 + df))
                else:
                    idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
                    norm = tf + 1.5 * (
                        1 - 0.75 + 0.75 * self.lengths[key] / max(self.average, 1)
                    )
                    scores[key] += idf * tf * 2.5 / norm

        def matches(key, phrase):
            return (
                any(
                    all(
                        start + i in self.postings.get(t, {}).get(key, [])
                        for i, t in enumerate(phrase)
                    )
                    for start in self.postings.get(phrase[0], {}).get(key, [])
                )
                if phrase
                else True
            )

        results = []
        for key, score in sorted(scores.items(), key=lambda x: (-x[1], x[0])):
            if all(matches(key, p) for p in phrases):
                d = self.documents[key]
                content = d["content"]
                at = next(
                    (content.lower().find(t) for t in terms if t in content.lower()), 0
                )
                start = max(0, at - 70)
                results.append(
                    {
                        **d,
                        "content": content[start : start + 260],
                        "score": round(score, 5),
                    }
                )
        return results[:limit]

    def suggest(self, prefix):
        return (
            sorted(
                (t for t in self.postings if t.startswith(prefix.lower())),
                key=lambda t: (-len(self.postings[t]), t),
            )[:7]
            if prefix
            else []
        )
