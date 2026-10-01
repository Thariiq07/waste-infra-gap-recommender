"""
dashboard/logic.py

Small, framework-free helpers used by dashboard/app.py. Kept separate from
app.py (which runs Streamlit UI code at import time) purely so this logic
can be unit tested directly with pytest, the same way api/clustering.py is
tested separately from api/main.py.
"""

from __future__ import annotations

# Priority tiers split the 0-1 underserved_index into three plain-language
# bands. Thresholds are simple terciles, not derived from the thesis itself
# (the thesis reports the raw score; this bucketing exists only to make the
# dashboard legible to a non-technical viewer).
HIGH_THRESHOLD = 0.66
MEDIUM_THRESHOLD = 0.33

PRIORITY_COLORS = {
    "High priority": "#c0392b",
    "Medium priority": "#e6a23c",
    "Lower priority": "#3f8f5f",
}


def priority_label(score: float) -> str:
    """Turn the 0-1 underserved_index into a plain-language priority tier."""
    if score >= HIGH_THRESHOLD:
        return "High priority"
    if score >= MEDIUM_THRESHOLD:
        return "Medium priority"
    return "Lower priority"


def priority_color(score: float) -> str:
    return PRIORITY_COLORS[priority_label(score)]
