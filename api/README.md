# api/

FastAPI service for the Waste Infrastructure Gap Recommender.

- `clustering.py` — K-Means (K=3) clustering and Underserved Index calculation,
  ported from the thesis notebook. Output verified against the thesis report's
  own results (cluster sizes 3/7/21 Urban/Commuter Belt/Rural, and Underserved
  Index scores for the five priority local authorities all match exactly).
- `main.py` — the FastAPI app itself.

## Endpoints

- `GET /clusters` — all 31 local authorities with their K-Means cluster assignment
- `GET /underserved-index` — all 31 ranked by Underserved Index, most underserved
  first (`?top=N` to limit)
- `GET /local-authority/{name}` — a single local authority's full result
  (case-insensitive, e.g. `/local-authority/cork-county`)

## Running locally

```
pip install -r requirements.txt
python data/ingest.py          # generates data/processed/*.csv, needed first
uvicorn api.main:app --reload
```

Then visit `http://127.0.0.1:8000/docs` for interactive API docs, or hit
the endpoints directly, e.g. `http://127.0.0.1:8000/underserved-index?top=5`.

## Tests

```
pytest
```
