"""
tests/test_live_api.py

Integration tests against the *deployed* API (Week 5), as opposed to
tests/test_api.py which exercises the app in-process. These hit a real URL
over the network, so they're skipped unless LIVE_API_URL is explicitly set -
regular `pytest` runs (local or CI) never touch the network, and nothing
breaks CI if the deployment is ever temporarily down.

Run against the live deploy:
    LIVE_API_URL=https://your-deployed-api.example.com pytest tests/test_live_api.py -v
"""

from __future__ import annotations

import os

import pytest
import requests

LIVE_API_URL = os.environ.get("LIVE_API_URL")

pytestmark = pytest.mark.skipif(
    not LIVE_API_URL,
    reason="LIVE_API_URL not set - skipping live deployment checks",
)


@pytest.fixture(scope="module")
def base_url() -> str:
    return LIVE_API_URL.rstrip("/")


def test_live_root_responds(base_url):
    response = requests.get(base_url, timeout=30)
    assert response.status_code == 200
    assert "endpoints" in response.json()


def test_live_clusters_returns_all_31_local_authorities(base_url):
    response = requests.get(f"{base_url}/clusters", timeout=30)
    assert response.status_code == 200
    assert len(response.json()) == 31


def test_live_underserved_index_top_5_matches_thesis_priority_areas(base_url):
    response = requests.get(f"{base_url}/underserved-index?top=5", timeout=30)
    assert response.status_code == 200
    names = {row["local_authority"] for row in response.json()}
    assert names == {
        "Dublin City",
        "Cork County",
        "Fingal",
        "South Dublin",
        "Dún Laoghaire-Rathdown",
    }
