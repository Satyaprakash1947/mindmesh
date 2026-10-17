# MindMesh Showcase Deployment

This repository can publish a public static demo with GitHub Pages. The demo uses the authored built-in learning content and stores progress per browser on that device. No API key, database, or hosting account other than the GitHub repository is required for this mode.

## Publish the static demo

1. Merge the deployment workflow into the repository's `main` branch.
2. In GitHub, open **Settings → Pages** and set **Build and deployment → Source** to **GitHub Actions**. A repository administrator must do this once.
3. Open **Actions → Publish showcase site** and confirm the run succeeds. It runs automatically on pushes to `main`; it can also be started manually with **Run workflow**.
4. Open the URL shown on the successful run's `github-pages` environment. For this repository, the expected address is `https://satyaprakash1947.github.io/mindmesh/`.

The Pages build runs frontend lint and production build before publishing. Its default API URL is empty in production, so the static showcase uses the built-in demo instead of trying to call a visitor's `localhost` API.

## Connect the live API (optional)

1. In Render, create a Blueprint from this repository and apply `render.yaml`. It uses Render's free web-service plan and starts in memory mode without external credentials. Free services can spin down after inactivity, so allow extra time for the first request after a quiet period. Render's `CORS_ORIGINS` is set to the GitHub Pages origin; if you use another domain, change it to that site's exact origin (scheme and host, no path).
2. Copy the API service URL from Render.
3. In GitHub, open **Settings → Secrets and variables → Actions → Variables**, then create `VITE_API_BASE_URL` with the API URL, such as `https://your-mindmesh-api.onrender.com`.
4. Run **Actions → Publish showcase site → Run workflow** on `main`. The build embeds the API URL and the published frontend will use the live API.

The live API can use the built-in graph and in-memory progress without credentials. This is suitable for a short demo; progress is isolated by a browser-generated student ID, but is lost when the service restarts. For persistent graph data, create a Neo4j Aura database, set `NEO4J_URI`, `NEO4J_USERNAME`, and `NEO4J_PASSWORD` in the Render service environment, then run `python scripts/seed.py` from `backend/` with those values in the local environment. Never put these credentials in GitHub variables, source files, or a Pages build.

Generated tutor explanations are optional. If configured, set `LLM_API_BASE`, `LLM_API_KEY`, and `LLM_MODEL` on the API service only. Without them, MindMesh uses its authored content and deterministic grader.

## Showcase checklist

- Confirm the deployed URL opens over HTTPS and the workspace loads.
- Start a learning session, answer a diagnostic question, and inspect Graph and Progress.
- If using the live API, open its `/api/health` endpoint and confirm the expected `graph_backend`.
- Use [the demo script](demo-script.md) to present the learning loop and explain whether the demo is in built-in or live API mode.
- Submit the deployed URL with the repository link and note that Aura and generated tutor content are optional integrations.
