# MindMesh

MindMesh is an adaptive learning tutor that maps a learner's question to a concept, diagnoses prerequisite gaps, teaches the missing concept, and recommends what to learn next. A Neo4j concept graph drives prerequisite paths and mastery; a local mock mode keeps the demo usable without external services.

## Project status

The repository includes the graph-driven learning loop, a deterministic rubric grader, an optional OpenAI-compatible tutor, and a React demo. The backend supports a seeded graph in memory and can connect to Neo4j Aura when configured. The frontend starts with local mock data and switches to the API when it is available. Hosting accounts and secrets are intentionally configured outside the repository.

## Architecture

```mermaid
flowchart LR
  Student[Student] --> UI[React tutor and graph UI]
  UI --> API[FastAPI]
  API --> Learning[Learning loop and answer grading]
  Learning --> Graph[Graph repository]
  Graph --> Neo4j[(Neo4j Aura)]
  Graph -. fallback .-> Seed[Seed graph in memory]
  Learning -. provider unavailable .-> Mock[Mock tutor]
```

## Repository layout

```text
backend/
  data/concepts.json    Versioned concepts and prerequisite edges
  app/
    ai/                 Tutor provider and mock fallback
    api/                Graph and learning routes
    graph/              Database helper, parameterized queries, mastery, repository
    models/             Shared API schemas
    main.py             FastAPI application
  scripts/seed.py       Seed the Neo4j concept graph
  tests/                API, graph, and learning-loop tests
frontend/
  src/
    api/                API client with mock fallback
    components/         Shared graph and status components
    pages/              Workspace, graph, tutor, quiz, progress
    types/              API contracts
docs/
  api-contract.md
  graph-schema.md
  demo-script.md
```

## Requirements

- Python 3.11+
- Node.js 20+
- Neo4j Aura database for persistent graph and attempt data (optional for local mock mode)

## Run locally

The quickest path uses the built-in concept graph and does not need any account, API key, or database. Start the backend and frontend in two terminals, then open `http://localhost:5173`.

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env  # Windows PowerShell: Copy-Item .env.example .env
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`; interactive API docs are at `/docs`. Without Neo4j credentials, it uses the built-in seed graph and in-memory attempts.

### Frontend

```bash
cd frontend
npm install
copy .env.example .env  # Windows PowerShell: Copy-Item .env.example .env
npm run dev
```

Open `http://localhost:5173` (or the Vite URL shown in the terminal). If the backend is unavailable, the frontend shows the seeded mock learning flow. Set `VITE_API_BASE_URL=http://localhost:8000` to use the API. The API also allows the Vite `127.0.0.1` origin for setups that use that URL.

### Run API and Neo4j with Docker Compose

Docker Compose starts a local Neo4j database, waits for it to become healthy, seeds the concept graph, and then starts the API:

```bash
docker compose up --build
```

Open `http://localhost:8000/docs` to explore the API. Start the frontend separately with the steps above. This Compose setup uses a development-only Neo4j password; do not reuse it outside your machine. The seed runs again safely whenever the seed container is recreated.

### Seed Neo4j Aura

Set `NEO4J_URI`, `NEO4J_USERNAME`, and `NEO4J_PASSWORD` in `backend/.env`, then run:

```bash
cd backend
python scripts/seed.py
```

The seed script is idempotent: it merges concept nodes and prerequisite edges by stable IDs.

## Learning flow

1. The learner enters a question or chooses a target concept.
2. MindMesh maps the question to a concept. Low-confidence matches ask the learner to choose a topic.
3. The API returns the prerequisite graph and a diagnostic question.
4. The learner's answer is graded against the concept rubric and saved as an attempt.
5. The response includes the score, feedback, matched rubric points, and missing rubric points. The graph updates mastery and recommends the nearest unmet prerequisite; after a successful retest it can recommend the original target.
6. Teaching material comes from the configured tutor provider when it returns valid content; missing credentials, invalid responses, timeouts, and provider errors use the authored local explanation and worked example.

Mastery states are `unknown`, `needs_review`, and `demonstrated`. No attempts means `unknown`; a latest score below 0.5 means `needs_review`; otherwise the mean of the latest two scores is compared with the default 0.7 threshold (`MASTERY_THRESHOLD`). The graph response explains why a prerequisite is next in `next_reason`.

## Graph and seed data

The source data in `backend/data/concepts.json` contains 15 concepts and 18 `REQUIRES` edges. An edge from A to B means A is a prerequisite for B. Each concept includes an original explanation, diagnostic question, worked example, and rubric. The Aura seed command creates uniqueness constraints and uses parameterized `MERGE` statements, so it is safe to run repeatedly. `docs/graph-schema.md` describes the node model, mastery rule, and recommendation behavior.

`GET /api/graph/{concept_id}?student_id=...` returns `{nodes, edges, target, next_concept, next_reason}`. It picks the closest unmet prerequisite whose own prerequisites are demonstrated, and returns a readable reason that Person 3 can display in the graph UI.

## API

See [the API contract](docs/api-contract.md). Main routes:

- `GET /api/health`
- `GET /api/concepts`
- `GET /api/graph/{concept_id}`
- `POST /api/learning/start`
- `POST /api/diagnose`
- `POST /api/answer`
- `POST /api/learning/next`
- `POST /api/mastery/update`

## Configuration and secrets

Copy the relevant `.env.example` files to `.env` for local development. Never commit `.env` files or real Neo4j/LLM credentials. Configure those values in GitHub Actions and the hosting provider's secret/environment settings.

| Goal | Required values or accounts |
| --- | --- |
| Run the frontend and API locally in built-in mode | None. Python and Node.js are installed locally; the API uses the bundled seed graph and in-memory attempts. |
| Use generated tutor explanations | Optional OpenAI-compatible provider credentials: `LLM_API_BASE`, `LLM_API_KEY`, and `LLM_MODEL`. Without them, the authored tutor content is used. |
| Persist graph and attempts in Neo4j | Optional Neo4j Aura instance (or local Docker Compose Neo4j) and `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`; `NEO4J_DATABASE` defaults to `neo4j`. Run the seed command once. |
| Publish a hosted demo | GitHub repository access plus hosting accounts for the frontend (Vercel) and API (Render), and a Neo4j Aura instance for persistence. Set the frontend API URL and API CORS/Neo4j values in the hosting dashboards. |

No GitHub token, LLM key, or Aura account is needed for local built-in mode. Do not paste secrets into GitHub issues, commits, or chat; add them only to local ignored `.env` files or the provider's secret settings. `CORS_ORIGINS` must contain the exact deployed frontend origin(s), comma-separated.

## Deploy

- The public showcase frontend deploys to GitHub Pages from `main` through `.github/workflows/pages.yml`. It runs in built-in demo mode without API keys.
- For a live API, deploy the included `render.yaml` Blueprint, then set the GitHub repository variable `VITE_API_BASE_URL` to the Render service URL. The Pages workflow will use it on its next run.
- Neo4j Aura is optional. Without it, the API uses in-memory demo progress. To persist graph attempts, configure Aura credentials in Render and run the seed script once.

See [the showcase deployment guide](docs/showcase-deployment.md) for setup, verification, and demo submission steps.

## Team workflow

Use short-lived `feat/...`, `fix/...`, and `chore/...` branches. Keep pull requests focused, update `docs/api-contract.md` when shared request/response shapes change, and review changes to the API contract with the whole team. Keep `main` deployable and require CI and review through repository branch protection settings.

See [the demo script](docs/demo-script.md) for the two-minute walkthrough and fallback steps.
