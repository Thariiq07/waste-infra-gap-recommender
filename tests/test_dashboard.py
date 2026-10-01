"""
tests/test_dashboard.py

Tests for the dashboard's framework-free logic (dashboard/logic.py) and for
the map boundaries file it depends on. Doesn't exercise the Streamlit UI
itself (that needs a running browser/session) - just the parts that can
silently break: the priority bucketing math, and the boundaries file
drifting out of sync with the 31 local authority names data/ingest.py
produces.
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd

from dashboard.logic import priority_color, priority_label

BOUNDARIES_PATH = Path(__file__).parent.parent / "data" / "raw" / "local_authority_boundaries.geojson"


def test_priority_label_bands():
    assert priority_label(0.0) == "Lower priority"
    assert priority_label(0.32) == "Lower priority"
    assert priority_label(0.33) == "Medium priority"
    assert priority_label(0.65) == "Medium priority"
    assert priority_label(0.66) == "High priority"
    assert priority_label(1.0) == "High priority"


def test_priority_color_is_consistent_with_label():
    # Every score should map to a color, and the same label should always
    # map to the same color (no silent typo between the two functions).
    for score in (0.0, 0.2, 0.33, 0.5, 0.66, 0.9, 1.0):
        label = priority_label(score)
        color = priority_color(score)
        assert color, f"no color for score {score}"
        assert priority_color(score) == priority_color(score)  # deterministic
        if label == "High priority":
            assert color == "#c0392b"
        elif label == "Medium priority":
            assert color == "#e6a23c"
        else:
            assert color == "#3f8f5f"


def test_boundaries_file_has_31_areas():
    gdf = gpd.read_file(BOUNDARIES_PATH)
    assert len(gdf) == 31
    assert "local_authority" in gdf.columns
    assert gdf.geometry.notna().all()


def test_boundaries_names_match_ingest_pipeline_names():
    """
    The dashboard merges the API's local_authority names onto this file's
    local_authority names with a plain equality join (see app.py) - if
    these ever drift apart, areas would silently vanish from the map
    instead of erroring, so this is checked explicitly.
    """
    from data.ingest import GEOGID_TO_LOCAL_AUTHORITY

    boundaries = gpd.read_file(BOUNDARIES_PATH)
    boundary_names = set(boundaries["local_authority"])
    expected_names = set(GEOGID_TO_LOCAL_AUTHORITY.values())

    assert boundary_names == expected_names


def test_boundaries_merge_with_processed_la_features(tmp_path):
    """Sanity check the actual merge app.py performs doesn't drop any rows."""
    la_features_path = Path(__file__).parent.parent / "data" / "processed" / "la_features.csv"
    if not la_features_path.exists():
        import data.ingest

        data.ingest.main()

    boundaries = gpd.read_file(BOUNDARIES_PATH)
    la_features = pd.read_csv(la_features_path)

    merged = boundaries.merge(la_features, on="local_authority", how="left")
    assert merged["total_households"].notna().all(), "some local authorities failed to merge"
    assert len(merged) == 31
