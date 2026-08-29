"""
api/clustering.py

Local Authority level K-Means clustering and Underserved Index calculation,
ported from the thesis notebook (Section 4.2 / cells 10-13 for clustering,
cells 21/31 for the Underserved Index).

This module is deliberately separate from data/ingest.py: ingest.py only
loads and cleans data, this module runs the actual analysis on top of it.
"""

from __future__ import annotations

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler, StandardScaler

CLUSTER_FEATURES = [
    "internet_rate",
    "professional_rate",
    "ownership_rate",
    "total_households",
]

# K=3 was chosen via the elbow method + silhouette score (0.372) in the
# thesis (Report, Section 6.2) — see the three-way Urban / Commuter Belt /
# Rural split that results, sized 3 / 7 / 21 local authorities.
N_CLUSTERS = 3
RANDOM_STATE = 42


def add_clusters(la_features: pd.DataFrame) -> pd.DataFrame:
    """
    Run K-Means (K=3) on the four LA-level proxy features and label each
    resulting cluster using the thesis's own naming (Report, Table 6),
    identified here by matching cluster size and professional_rate rather
    than assuming a fixed sklearn label order (KMeans cluster indices 0/1/2
    aren't guaranteed to line up with the report's Urban/Commuter/Rural
    ordering run to run).
    """
    df = la_features.copy()

    X = StandardScaler().fit_transform(df[CLUSTER_FEATURES])
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
    df["cluster_id"] = kmeans.fit_predict(X)

    sizes = df["cluster_id"].value_counts()
    profile = df.groupby("cluster_id")[["professional_rate", "ownership_rate"]].mean()

    # Urban: smallest cluster (n=3 in the thesis). Commuter Belt: highest
    # professional_rate and ownership_rate among the remaining two. Rural:
    # whatever's left.
    urban_id = sizes.idxmin()
    remaining = [c for c in sizes.index if c != urban_id]
    commuter_id = profile.loc[remaining, "professional_rate"].idxmax()
    rural_id = [c for c in remaining if c != commuter_id][0]

    label_map = {urban_id: "Urban", commuter_id: "Commuter Belt", rural_id: "Rural"}
    df["cluster_label"] = df["cluster_id"].map(label_map)

    return df


def add_underserved_index(la_features_with_facilities: pd.DataFrame) -> pd.DataFrame:
    """
    Underserved Index (Report, Section 4.6): computed independently of the
    K-Means clusters above, from professional_rate + total_households
    (generation potential) versus facility_count per 1,000 households
    (coverage). 1 = most underserved, 0 = least.

    Expects a DataFrame with professional_rate, total_households, and
    facility_count columns already present (i.e. LA features merged with
    data/ingest.py's facility_counts.csv).
    """
    df = la_features_with_facilities.copy()
    scaler = MinMaxScaler()

    df["ewaste_potential"] = scaler.fit_transform(
        df[["professional_rate", "total_households"]].mean(axis=1).values.reshape(-1, 1)
    )

    df["facilities_per_1000hh"] = (df["facility_count"] / df["total_households"]) * 1000
    df["coverage_score"] = scaler.fit_transform(
        df["facilities_per_1000hh"].values.reshape(-1, 1)
    )

    df["underserved_index"] = (df["ewaste_potential"] - df["coverage_score"] + 1) / 2

    return df


def build_la_analysis(
    la_features: pd.DataFrame, facility_counts: pd.DataFrame
) -> pd.DataFrame:
    """Full LA-level analysis: clusters + Underserved Index in one table."""
    merged = la_features.merge(
        facility_counts[["geogid", "facility_count"]], on="geogid", how="left"
    )
    merged = add_clusters(merged)
    merged = add_underserved_index(merged)
    return merged
