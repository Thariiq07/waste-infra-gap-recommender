# Waste Infrastructure Gap Recommender

**Turning a Master's thesis into a live, queryable tool.**

## The problem

Ireland's e-waste recycling infrastructure isn't evenly distributed relative to where waste is actually generated. My Master's thesis — *Multi-Scale Spatial Clustering Framework for E-Waste Infrastructure Planning* (AI & Machine Learning, University of Limerick) — built a data-driven "Underserved Index" across all 3,417 electoral divisions in Ireland to find exactly where that mismatch is worst.

The headline finding: **four local authorities show high e-waste generation potential and zero licensed facilities** — Cork County, Fingal, South Dublin, and Dún Laoghaire-Rathdown.

That analysis lived in a PDF and a set of notebooks. This project turns it into something anyone — a recruiter, a council planner, a researcher — can query and explore live in a browser, instead of reading a report.

## Architecture

```
                 ┌─────────────────┐
   CSO Census    │                  │
   Pobal HP Index│   data/ingest.py │──── cleaned, versioned
   EPA Facilities│  (pipeline)      │     datasets
                 └─────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  K-Means + SOM   │  clustering &
                 │  clustering      │  cross-validation
                 └─────────────────┘
                          │
                          ▼
                 ┌─────────────────┐        ┌──────────────────┐
                 │   FastAPI (api/) │◄──────►│ Streamlit         │
                 │  /clusters       │        │ dashboard/        │
                 │  /underserved-idx│        │ (interactive map) │
                 │  /local-authority│        └──────────────────┘
                 └─────────────────┘
                          │
                 Dockerized · CI (GitHub Actions)
                 Deployed: API → Render/Fly.io
                           Dashboard → Streamlit Community Cloud
```

## Status

🚧 **Week 1 of 6 — Scaffold & data.** See [Issues](../../issues) for the full 6-week roadmap.

| Week | Focus | Status |
|---|---|---|
| 1 | Repo scaffold + data ingestion | In progress |
| 2 | FastAPI service + tests | Planned |
| 3 | Docker + CI/CD | Planned |
| 4 | Streamlit dashboard | Planned |
| 5 | Deploy API + wire up live dashboard | Planned |
| 6 | Polish, docs, demo link | Planned |

## Repo layout

```
.
├── api/          FastAPI service (clustering + Underserved Index endpoints)
├── dashboard/    Streamlit app (interactive choropleth map)
├── data/         Ingestion pipeline for CSO / Pobal / EPA datasets
├── tests/        pytest suite for the API
└── .github/      CI workflows
```

## Methodology (from the thesis)

- **Data:** CSO Census 2022 (793 raw variables, reduced to the 4 most explanatory), Pobal HP Deprivation Index, EPA Licensed Waste Facility register.
- **Clustering:** K-Means found a clean 3-cluster socioeconomic structure across Ireland's electoral divisions.
- **Validation:** independently cross-checked with a Self-Organizing Map (SOM) built from scratch — the two methods agreed with an Adjusted Rand Index of 0.43, which is what gave confidence to build a real tool on top of the result rather than leave it as a single-algorithm finding.

## Live demo

_Coming in Week 5 — link will go here once the API and dashboard are deployed._

## Running locally

_Instructions will be added as each service comes online (Week 2 onward)._

## License

MIT
