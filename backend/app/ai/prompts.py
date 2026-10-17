DIAGNOSTIC_PROMPT = """Ask one short diagnostic question about the named concept. Test understanding, not memorization. Do not reveal the answer. Return JSON with a question string."""

EXPLANATION_PROMPT = """Explain the named concept to a student in plain language. Use the supplied reference as ground truth. Keep it concise and avoid introducing unsupported facts."""

WORKED_EXAMPLE_PROMPT = """Give one short worked example for the named concept. Show the important steps and state the result. Use the supplied reference example as ground truth."""

FEEDBACK_PROMPT = """Compare the student's response with the rubric. Return a score from 0 to 1, one encouraging sentence of feedback, and the missing rubric points. Do not mark a response correct if it omits the core idea."""

TUTOR_SYSTEM_PROMPT = f"{EXPLANATION_PROMPT}\n{WORKED_EXAMPLE_PROMPT}\nReturn JSON with explanation and worked_example strings."
