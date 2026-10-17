Each person owns one layer of the product, so nobody is blocked waiting for someone else.
Person C is also the repo admin and team lead. They merge to main, keep the API contract current, and own the final demo.
- Set up Neo4j Aura and write the schema: Concept, Student, Attempt, with REQUIRES, HAS_ATTEMPT and FOR_CONCEPT relationships.
- Write the seed script for the gradient descent graph (Functions → Slope → Derivatives → Gradient → Gradient Descent). Include 10–15 concepts, each with an explanation, a diagnostic question and a rubric or answer key.
- Write the Cypher queries: prerequisite paths, nearest missing prerequisite, and mastery calculation from recent attempts.
- Build the graph endpoints: GET /api/graph/{concept_id} and the mastery update.
- Write tests proving that changing mastery changes the recommended path.
Deliverable: seed.py, the graph/ module, and tested queries that return structured JSON (nodes with id, name, status; edges with source, target).
- Map the student’s question to a concept ID, and fall back to asking the student to pick a topic when confidence is low.
- Write the prompts for diagnostic questions, explanations, worked examples and feedback.
- Grade answers against the rubric, returning a score and feedback as structured JSON.
- Write the decision logic for diagnose → find the gap → teach → retest → return to the original topic.
- Expose the endpoints: /api/learning/start, /api/diagnose, /api/answer and /api/learning/next.
- Add a mock-LLM fallback so the demo works if the API fails or rate-limits.
Deliverable: a working diagnosis → teach → retest loop, driven by the student’s answers rather than hardcoded.
- Scaffold the repo, CI, branch protection, issue board and docs/api-contract.md in the first 30 minutes.
- Build the four screens: workspace, graph (React Flow), tutor and quiz, and progress and next step.
- Style nodes by status: unknown (grey), needs_review (red), demonstrated (green), and highlight the current target.
- Start on mock JSON so the frontend never waits for the backend, then swap in the real API.
- Deploy the frontend on Vercel and the backend on Render or Railway, and manage the environment variables.
- Run end-to-end tests of the full journey, and prepare the demo script, slides and fallback data.
Deliverable: a deployed, tested web app and the two-minute demo.
```
mindmesh/
├── README.md
├── .github/
│   ├── workflows/ci.yml
│   ├── pull_request_template.md
│   ├── ISSUE_TEMPLATE/
│   └── CODEOWNERS
├── docs/
│   ├── api-contract.md
│   ├── graph-schema.md
│   └── demo-script.md
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/          # routes (shared, small PRs)
│   │   ├── graph/        # Person A
│   │   ├── ai/           # Person B
│   │   └── models/       # shared Pydantic schemas
│   ├── scripts/seed.py   # Person A
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
└── frontend/             # Person C
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── api/          # API client + mock data
    │   └── types/
    ├── package.json
    └── .env.example
```
CODEOWNERS makes review requests automatic:
```
/backend/app/graph/   @personA
/backend/scripts/     @personA
/backend/app/ai/      @personB
/frontend/            @personC
/docs/                @personC
/.github/             @personC
```
Branching. Use trunk-based development with short-lived branches, which is simpler than Git Flow for a sprint.
- main is always deployable and protected: no direct pushes, a PR with 1 approval is required, and CI must pass.
- Branch names: feat/graph-prereq-query, feat/ai-diagnosis, feat/ui-graph-view, fix/..., chore/...
- Keep branches under a few hours old, and merge small and often.
Commits. Use Conventional Commits: feat(graph): add prerequisite path query, fix(ai): handle empty rubric, docs: update api contract.
Pull requests.
- One PR is one focused change, ideally under 300 lines.
- Another team member reviews it, with a target response time of 15 minutes during the sprint.
- Use squash merge to keep history clean.
- The PR template should include: what changed, why, how to test, screenshots (for UI), and a checklist (tests pass, no secrets, contract updated).
Issues and board. Create a GitHub Project with the columns Backlog → In Progress → In Review → Done. Label issues graph, ai, frontend, infra and bug, and assign each issue to one owner.
CI (GitHub Actions). On every PR:
- Backend: ruff (lint) and pytest
- Frontend: eslint and npm run build
Security. Never commit .env files. Commit .env.example with placeholder values only. Neo4j and LLM keys go in GitHub Secrets and in the hosting platform’s environment settings. Rotate any key that is ever accidentally pushed.
Person C writes this in the first 30 minutes, and the whole team signs off before coding starts. Changes after that require a PR to docs/api-contract.md, which everyone reviews.
Example shared shapes:
json
```json
// GET /api/graph/{concept_id}
{
  "nodes": [{"id": "derivatives", "name": "Derivatives", "status": "needs_review"}],
  "edges": [{"source": "slope", "target": "derivatives", "type": "REQUIRES"}],
  "target": "gradient_descent"
}

// POST /api/answer
{ "student_id": "s1", "concept_id": "derivatives", "answer": "..." }
// response
{ "score": 0.3, "feedback": "...", "status": "needs_review", "next_concept": "derivatives" }
```
Status values are unknown, needs_review and demonstrated. Everyone uses exactly these.
Merge checkpoints (everyone merges and pulls): at 1:30, 2:30 and 3:30. Don’t let branches drift past these points.
1. Stay inside your own folder. Touch someone else’s code only through a PR they review.
2. Shared files (models/, api/, api-contract.md) change only through small, quick PRs.
3. Pull from main before starting any new task.
4. If you’re blocked, say so right away. Don’t wait.
5. Don’t hardcode the diagnosis. The student’s answer must decide the gap.
- Neo4j holds real concepts and prerequisite relationships.
- Selecting a target concept shows its prerequisite graph.
- A wrong diagnostic answer marks a prerequisite as needs_review.
- A correct retest changes it to demonstrated and changes the next recommendation.
- The deployed app works end to end, with a README that has setup steps, an architecture diagram and a demo link.
