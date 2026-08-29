"""
api/main.py

FastAPI service for the Waste Infrastructure Gap Recommender.

Serves the Local Authority level clustering and Underserved Index results
computed in api/clustering.py, from the data cleaned by data/ingest.py.

Run:
    uvicorn api.main:app --reload

Then visit http://127.0.0.1:8000/docs for interactive API docs (FastAPI
generates this automatically).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from api.clustering import build_la_analysis

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

app = FastAPI(
    title="Waste Infrastructure Gap Recommender API",
    description=(
        "Local Authority level e-waste infrastructure gap analysis, "
        "ported from a Master's thesis on spatial clustering."
    ),
    version="0.1.0",
)


class LocalAuthority(BaseModel):
    geogid: str
    local_authority: str
    cluster_label: str
    internet_rate: float
    professional_rate: float
    ownership_rate: float
    total_households: int
    facility_count: int
    underserved_index: float


@lru_cache
def _load_analysis() -> pd.DataFrame:
    """
    Load the processed LA features + facility counts and run the clustering
    / Underserved Index analysis once, cached for the process lifetime.

    Raises a clear error at request time (not import time) if
    `python data/ingest.py` hasn't been run yet.
    """
    la_path = PROCESSED_DIR / "la_features.csv"
    fac_path = PROCESSED_DIR / "facility_counts.csv"

    if not la_path.exists() or not fac_path.exists():
        raise FileNotFoundError(
            "Processed data not found. Run `python data/ingest.py` first "
            "to generate data/processed/la_features.csv and facility_counts.csv."
        )

    la_features = pd.read_csv(la_path)
    facility_counts = pd.read_csv(fac_path)
    return build_la_analysis(la_features, facility_counts)


def _get_analysis() -> pd.DataFrame:
    try:
        return _load_analysis()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


def _row_to_model(row: pd.Series) -> LocalAuthority:
    return LocalAuthority(
        geogid=row["geogid"],
        local_authority=row["local_authority"],
        cluster_label=row["cluster_label"],
        internet_rate=row["internet_rate"],
        professional_rate=row["professional_rate"],
        ownership_rate=row["ownership_rate"],
        total_households=int(row["total_households"]),
        facility_count=int(row["facility_count"]),
        underserved_index=row["underserved_index"],
    )


@app.get("/")
def root() -> dict:
    return {
        "name": "Waste Infrastructure Gap Recommender API",
        "endpoints": ["/clusters", "/underserved-index", "/local-authority/{name}"],
        "docs": "/docs",
    }


@app.get("/clusters", response_model=list[LocalAuthority])
def get_clusters() -> list[LocalAuthority]:
    """All 31 local authorities with their K-Means cluster (K=3) assignment."""
    df = _get_analysis()
    return [_row_to_model(row) for _, row in df.iterrows()]


@app.get("/underserved-index", response_model=list[LocalAuthority])
def get_underserved_index(top: int | None = None) -> list[LocalAuthority]:
    """
    All 31 local authorities ranked by Underserved Index, most underserved
    first. Pass ?top=N to limit to the N highest-scoring areas.
    """
    df = _get_analysis().sort_values("underserved_index", ascending=False)
    if top is not None:
        df = df.head(top)
    return [_row_to_model(row) for _, row in df.iterrows()]


@app.get("/local-authority/{name}", response_model=LocalAuthority)
def get_local_authority(name: str) -> LocalAuthority:
    """
    A single local authority's clustering + Underserved Index result,
    looked up by name (case-insensitive, spaces/hyphens interchangeable,
    e.g. "cork-county" or "Cork County" or "cork county" all match).
    """
    df = _get_analysis()

    normalised = name.strip().lower().replace("-", " ")
    matches = df[df["local_authority"].str.lower() == normalised]

    if matches.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No local authority found matching '{name}'.",
        )

    return _row_to_model(matches.iloc[0])
