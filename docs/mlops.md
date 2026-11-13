# MLOps operating model

Applied from [MLOps Principles](https://ml-ops.org/content/mlops-principles), maintained by INNOQ and credited to its listed authors. This project implements a lightweight engineering baseline, not a claim of production readiness or an assigned ML Test Score.

## Implemented controls

| Concern | Concrete implementation |
|---|---|
| Code/data/configuration lineage | Git commit, application SHA-256, runtime/analysis lock hashes, corpus or generated-dataset fingerprint, configuration hash |
| Experiment records | `python -m app.experiments` writes immutable JSON run records with configuration, metrics and gate decisions |
| Data/model checks | Schema and algorithm regression tests plus project-specific offline evaluation gates |
| Notebook reproducibility | `scripts/check_notebooks.py` validates source/output structure; `--execute` runs every notebook in a fresh kernel |
| Release automation | GitHub CI installs pinned dependencies, runs tests/evaluations/notebooks and uploads reproducibility records |
| Operational monitoring | `/api/ops` exposes bounded status/latency summaries and configurable alerts; no request payloads are logged there |
| Environment parity | Runtime lock used in Docker; dev/analysis lock used for notebook/test work; container context excludes secrets and runtime data |
| Rollback | Revert reviewed code/configuration and the corresponding model/index artifact, then run canaries |

## Commands

```bash
python -m pip install -r requirements.lock
python -m pytest -q
python -m app.experiments --output artifacts/release
python scripts/check_notebooks.py
# In a normal environment with Jupyter kernels available:
python scripts/check_notebooks.py --execute
```

`artifacts/` and runtime SQLite databases are ignored by Git. Experiment records never contain API keys. Notebook CI uses bundled demo data and mocked providers, with no paid API requests. Local notebook executions in this workspace use isolated IPython processes because socket-based kernels are unavailable; saved outputs are real executions.

`GET /api/version` identifies the code/data/environment. `GET /api/ops` reports the latest 1,000 recorded API requests, retaining at most 10,000 event rows. Monitoring checks alerts only after 20 samples. Latency budgets and error thresholds live in `ops/policy.json`; they are initial operational targets, not measured service guarantees. These are local single-service metrics, not a distributed monitoring system. Protect operations endpoints with the same access boundary as serving endpoints.

## Lumen-specific controls

`python -m app.experiments --output artifacts/runs` checks corpus schema/URL uniqueness, phrase ordering and fixed-query MRR for both BM25 and TF-IDF. The small six-query corpus is a regression fixture, not a real-world ranking benchmark. Records include corpus and configuration hashes, judgments and algorithm metrics.

Every live index rebuild computes a content fingerprint. Search responses and `/api/stats` expose `index_version`, so a ranking result can be tied to the exact indexed document set. The seed-corpus hash in `/api/version` and the runtime-index hash serve different purposes. After a crawl, use the runtime hash.

To roll back, restore a consistent database snapshot and the prior code/runtime lock, then restart to rebuild the in-memory index. Verify a fixed canary query, phrase ordering and the index version. Back up a live SQLite database through its backup API while writes are controlled; copying an active database file alone is not a consistent snapshot.

Operational monitoring records route templates, latency and status without query strings. The separate search-analytics feature intentionally stores local query history; control access and retention before multi-user deployment. External relevance judgments, larger corpora, concurrent load, incremental indexing and hardened crawler egress remain future work.

## Release procedure

1. Change one use case or hypothesis at a time. Record the data/configuration and evaluation question.
2. Run data, domain, integration and notebook checks against the locked environment.
3. Inspect experiment metrics and gates; document limitations. Keep failed candidates as experiment records rather than deploying them.
4. Review the exact code/artifact version and deploy to a restricted environment. Keep the previous version available.
5. Run canaries, inspect operational telemetry and evaluate quality with independent labels or judgments when available.
6. Roll back on failed canaries or unexplained regressions. Start another evaluated experiment rather than retraining blindly.

No automatic retraining, scheduled jobs, model promotion, public access change or new infrastructure purchase is configured. CI is configured in source; execution on GitHub depends on the account's Actions/billing status. Real-data governance, multi-user security, high availability, independent quality labels and larger-scale validation remain explicit deployment work.
