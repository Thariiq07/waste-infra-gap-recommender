"""
tests/conftest.py

Ensures data/processed/*.csv exists before the API test suite runs, so
`pytest` works standalone without requiring a manual `python data/ingest.py`
step first (CI in Week 3 will rely on this too).
"""

from pathlib import Path

import pytest

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"


@pytest.fixture(scope="session", autouse=True)
def ensure_processed_data():
    required = ["la_features.csv", "ed_features.csv", "facility_counts.csv"]
    if not all((PROCESSED_DIR / f).exists() for f in required):
        from data.ingest import main as run_ingest

        run_ingest()
