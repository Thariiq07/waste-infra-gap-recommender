"""
tests/test_api.py

pytest suite for the FastAPI service (Week 2, Issue 1's checklist item).

Run:
    pytest

Requires data/processed/*.csv to exist first — run `python data/ingest.py`
before running these tests (the API reads that processed data, same as it
would in production).
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_root_lists_endpoints():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "/clusters" in body["endpoints"]
    assert "/underserved-index" in body["endpoints"]
    assert "/local-authority/{name}" in body["endpoints"]


def test_clusters_returns_all_31_local_authorities():
    response = client.get("/clusters")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 31
    # Every row should have a cluster label from the K=3 result.
    assert {row["cluster_label"] for row in body} <= {"Urban", "Commuter Belt", "Rural"}


def test_clusters_cluster_sizes_match_thesis():
    """The thesis reports a 3 / 7 / 21 Urban / Commuter Belt / Rural split."""
    response = client.get("/clusters")
    body = response.json()
    sizes = {}
    for row in body:
        sizes[row["cluster_label"]] = sizes.get(row["cluster_label"], 0) + 1
    assert sizes == {"Urban": 3, "Commuter Belt": 7, "Rural": 21}


def test_underserved_index_is_sorted_most_underserved_first():
    response = client.get("/underserved-index")
    assert response.status_code == 200
    body = response.json()
    scores = [row["underserved_index"] for row in body]
    assert scores == sorted(scores, reverse=True)


def test_underserved_index_top_param_limits_results():
    response = client.get("/underserved-index?top=5")
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_underserved_index_top_5_matches_thesis_priority_areas():
    """
    The thesis's headline finding (Report, Table 11): Dublin City, Cork
    County, Fingal, South Dublin and Dún Laoghaire-Rathdown are the five
    highest-scoring local authorities.
    """
    response = client.get("/underserved-index?top=5")
    names = {row["local_authority"] for row in response.json()}
    assert names == {
        "Dublin City",
        "Cork County",
        "Fingal",
        "South Dublin",
        "Dún Laoghaire-Rathdown",
    }


def test_local_authority_lookup_happy_path():
    response = client.get("/local-authority/Cork County")
    assert response.status_code == 200
    body = response.json()
    assert body["local_authority"] == "Cork County"
    assert body["facility_count"] == 0


def test_local_authority_lookup_is_case_and_hyphen_insensitive():
    response = client.get("/local-authority/cork-county")
    assert response.status_code == 200
    assert response.json()["local_authority"] == "Cork County"


def test_local_authority_lookup_not_found():
    response = client.get("/local-authority/nonexistent-place")
    assert response.status_code == 404
    assert "nonexistent-place" in response.json()["detail"]
