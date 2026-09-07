# Dockerfile
#
# Builds and runs the FastAPI service. Two-stage flow inside a single image:
# 1. `python data/ingest.py` cleans the committed raw data into
#    data/processed/ (this happens at container *start*, not build time -
#    see CMD below - so a rebuilt image always reflects the current
#    ingest.py logic without needing a separate build step).
# 2. uvicorn serves the API.
#
# Build:  docker build -t waste-infra-gap-recommender .
# Run:    docker run -p 8000:8000 waste-infra-gap-recommender
# Then:   http://localhost:8000/docs

FROM python:3.11-slim

# geopandas needs GDAL at runtime; the geopandas/pyogrio wheels bundle their
# own copy on Linux, so no extra system packages are required here.

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ api/
COPY data/ data/

EXPOSE 8000

CMD ["sh", "-c", "python data/ingest.py && uvicorn api.main:app --host 0.0.0.0 --port 8000"]
