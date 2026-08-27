# GitHub Issues — Weeks 2-6 (create these once the repo is live)

Copy each block below into a new Issue on GitHub (Issues tab → New issue). Title is the first line, everything after is the issue body.

---

### Issue 1: Week 2 — Build the FastAPI service

**Labels:** week-2, api

Wrap the thesis's K-Means + SOM clustering output behind a FastAPI service.

**Endpoints:**
- `GET /clusters` — returns the 3-cluster socioeconomic structure per electoral division
- `GET /underserved-index` — returns the Underserved Index score per electoral division
- `GET /local-authority/{name}` — returns clustering + index results filtered to one local authority

**Tasks:**
- [ ] Load the cleaned data from `data/ingest.py` output
- [ ] Implement the three endpoints above
- [ ] Add request/response models with Pydantic
- [ ] Write a local pytest suite covering all three endpoints (happy path + not-found case)
- [ ] Update README "Running locally" section with API run instructions

---

### Issue 2: Week 3 — Containerize the API and set up CI

**Labels:** week-3, devops

**Tasks:**
- [ ] Write a `Dockerfile` for the API
- [ ] Write `docker-compose.yml` for local dev (API + any future services)
- [ ] Add a GitHub Actions workflow (`.github/workflows/ci.yml`) that installs deps, runs `ruff` lint, and runs `pytest` on every push and PR
- [ ] Add the CI status badge to the top of the README

---

### Issue 3: Week 4 — Build the Streamlit dashboard

**Labels:** week-4, dashboard

**Tasks:**
- [ ] Streamlit app in `dashboard/` that calls the FastAPI service
- [ ] Render the existing Folium/GeoPandas choropleth map interactively
- [ ] Add a local-authority filter/dropdown
- [ ] Deploy to Streamlit Community Cloud (free tier)
- [ ] Add a screenshot of the dashboard to the README

---

### Issue 4: Week 5 — Deploy the API and wire up the live dashboard

**Labels:** week-5, deploy

**Tasks:**
- [ ] Deploy the FastAPI service to Render or Fly.io (free tier)
- [ ] Point the deployed Streamlit dashboard at the live API URL (not localhost)
- [ ] Add 1-2 integration tests that hit the deployed endpoint
- [ ] Add the live demo link to the README

---

### Issue 5: Week 6 — Polish for recruiters

**Labels:** week-6, docs

**Tasks:**
- [ ] Rewrite README: problem statement, architecture diagram, live demo link, screenshot/GIF, Methodology section, Results section (the four underserved local authorities)
- [ ] Add a one-line description + topics/tags to the GitHub repo settings (e.g. `python`, `fastapi`, `machine-learning`, `geospatial`, `streamlit`)
- [ ] Add the project to resume Projects section and LinkedIn Featured section with live demo link
- [ ] Write the "we shipped it" LinkedIn post

---

## Optional Issue 6 (stretch, week 7-8): keep the repo active

- [ ] Add a simple auth-protected admin endpoint
- [ ] Add MLflow experiment tracking around the clustering step
