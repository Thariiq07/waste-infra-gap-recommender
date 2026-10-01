# dashboard/

The plain-language layer on top of the API. Where `api/` answers questions
in JSON for other programs, this is a normal web page: a colour-coded map
of Ireland's 31 local authorities plus a lookup box, built with
[Streamlit](https://streamlit.io/).

## Running it locally

The dashboard needs the API running first, in a separate terminal:

```
uvicorn api.main:app --reload
```

(or `docker compose up`, which does the same thing). Then, in another
terminal:

```
pip install -r requirements.txt
streamlit run dashboard/app.py
```

It opens automatically in your browser at `http://localhost:8501`. If the
API isn't reachable, the page shows a plain-English error instead of
crashing.

## Files

- `app.py` - the Streamlit page itself: fetches results from the API,
  merges them with `data/raw/local_authority_boundaries.geojson` for the
  map shapes, and renders the map, the lookup box, and the ranked table.
- `logic.py` - small framework-free helper functions (the "how underserved
  is this counted as, in plain words" bucketing). Kept separate from
  `app.py` so it can be unit tested directly, the same way
  `api/clustering.py` is tested separately from `api/main.py`.

## Pointing it at a different API

By default the dashboard calls `http://localhost:8000`. To point it
somewhere else (e.g. a deployed API - see the root README), set
`WASTE_API_URL` before launching:

```
WASTE_API_URL=https://your-deployed-api.example.com streamlit run dashboard/app.py
```
