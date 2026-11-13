# Verification record

Verified on 13 November 2026 with Python 3.12.

- 6 pytest regression tests passed.
- Python source compilation passed.
- DOM integration checks passed for rendered metrics, primary form submission, result rendering, error states, text escaping and button reset.
- All notebook code cells executed in an isolated IPython process and saved with outputs. Socket-based Jupyter kernels were unavailable in the build environment; the notebooks retain a normal Python 3 kernelspec for local Jupyter use.
- Browser connection timed out; pixel-level browser rendering and mobile interactions have not been visually verified. Responsive CSS breakpoints are implemented.
- HTTP integration tests use FastAPI TestClient. No public deployment is included.

## Measured results

The notebook evaluates BM25 and TF-IDF against six hand-labelled queries over twelve original documents, reporting reciprocal rank, recall@5 and in-process latency. Exact phrase ordering, unknown terms, ranking, persistent URL deduplication, query analytics and private-IP crawl restrictions are tested. **No external website crawl was performed**; a host must be enabled explicitly. The small corpus does not establish internet-scale quality or performance.

## Reproduce

Install `requirements.lock`, then run `python -m pytest -q`. Install Node 24+, run `npm ci && npm run test:ui`. Open the notebook in Jupyter and run all cells. See README for ports and configuration.

## Notebook and Tailwind update

Three substantive notebooks (15 executed code cells) now cover baseline analysis, deeper experiments and operational audits. All code cells executed with saved outputs; no error outputs remain. Tailwind CSS 4.3.5 builds successfully. DOM workflow checks pass after the UI changes. GitHub notebook inclusion is explicitly enabled without overriding its detected language; only compiler-generated CSS is marked generated.

## MLOps update

Release fingerprints, experiment gates, bounded operational telemetry and fresh-kernel notebook CI are implemented. Validation records are generated under ignored `artifacts/`; they are not claims that GitHub CI has executed. See `docs/mlops.md` for exact scope and deployment limits.

Final MLOps validation: 3 notebooks, 16 executed code cells; regression tests and project evaluation gates pass locally. Hosted Atlas uses real NVIDIA inference; provider completion IDs are recorded separately from mocked tests.
