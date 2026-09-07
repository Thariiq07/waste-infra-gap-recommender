# data/

`ingest.py` — a standalone, documented script that ports the thesis's data-cleaning
pipeline (CSO Census 2022, Pobal HP Deprivation Index, EPA Licensed Waste Facility
register) out of the original Colab notebook.

The three small source files (~700KB total: two CSVs and the EPA facilities zip) are
committed in `data/raw/` on purpose — they're public, open government data (CSO,
Pobal, EPA), and CI/Docker both need real input data to run the pipeline end-to-end
without you having to supply anything. Only the *generated* output
(`data/processed/`) is gitignored.

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

These three outputs are exactly what the FastAPI service (`api/`) serves, via the
clustering and Underserved Index logic in `api/clustering.py`.
