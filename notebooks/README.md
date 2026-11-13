# Notebook-led engineering analysis

Run these notebooks in numerical order with a Python 3 kernel. They import the same domain/services used by the application; they are executable analysis, not screenshots or inflated language-statistic files.

- [01 retrieval evaluation](01_retrieval_evaluation.ipynb)
- [02 index and ranking mechanics](02_index_and_ranking_mechanics.ipynb)
- [03 relevance and crawler audit](03_relevance_and_crawler_audit.ipynb)

Install `requirements.lock`, then `python -m pip install jupyterlab` and `python -m jupyter lab notebooks`. Start from a fresh kernel and Run All. Checked-in outputs come from real executions. All notebooks use local synthetic data, fixed source corpora, mocked providers or local API clients unless explicitly configured otherwise. No live NVIDIA key is used by default.
