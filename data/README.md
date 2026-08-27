# data/

`ingest.py` — a standalone, documented script that ports the thesis's data-cleaning
pipeline (CSO Census 2022, Pobal HP Deprivation Index, EPA Licensed Waste Facility
register) out of the original Colab notebook.

Raw data files are gitignored — only the ingestion code is versioned. Drop your own
copies of the three source files/zip into `data/raw/` to run it locally (or use the
copies already there if you got this repo as a zip from Claude).

**Status: all three sources ported and verified** against the thesis report's own
results — output matches Table 11 of the dissertation report exactly:

| Local Authority | Households (script) | Households (report) | Facilities (script) | Facilities (report) |
|---|---|---|---|---|
| Dublin City | 225,685 | 225,685 | 7 | 7 |
| Cork County | 127,971 | 127,971 | 0 | 0 |
| Fingal | 107,846 | 107,846 | 0 | 0 |
| South Dublin | 100,364 | 100,364 | 0 | 0 |
| Dún Laoghaire-Rathdown | 85,128 | 85,128 | 0 | 0 |

Run:
```
pip install pandas geopandas
python data/ingest.py
```

Produces:
- `data/processed/la_features.csv` — 31 local authorities × 4 proxy features
- `data/processed/ed_features.csv` — 3,417 electoral divisions × 5 proxy features
- `data/processed/facility_counts.csv` — e-waste-relevant licensed facility count per
  local authority

These three outputs are exactly what Week 2's FastAPI endpoints will serve, and what
the clustering/Underserved Index logic (also ported from the notebook, not yet wired
up here) will run on top of.
