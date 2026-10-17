# Two-minute demo script

## Setup

1. Start the backend and frontend using the README instructions. Neo4j is optional; the built-in seed graph is enough for the demo.
2. Open the workspace and choose **Gradient Descent** or ask, “How do I use gradient descent to minimize a function?”
3. If the topic picker appears, choose Gradient Descent.

## Walkthrough (about two minutes)

1. **Workspace (20 sec):** Show the target concept and prerequisite graph. Point out that status is learner-specific.
2. **Diagnose (25 sec):** Start a session and answer the derivative diagnostic incorrectly. Show the score, feedback, and `needs_review` status.
3. **Teach (25 sec):** Open the tutor explanation and worked example for the missing prerequisite.
4. **Retest (25 sec):** Submit a correct answer. Show the concept changing to `demonstrated` and the next recommendation updating.
5. **Return to target (15 sec):** Request the next step and show the path moving back toward Gradient Descent.
6. **Fallback (10 sec):** Stop the API or explain that the frontend's local mock dataset keeps the screens usable when the API is unavailable.

## Fallback data

The seed data includes a Functions → Slope → Derivatives → Gradient → Gradient Descent path. If live API access fails, the UI uses local concepts and a mock diagnosis/answer loop. Mention when the demo is using mock data.
