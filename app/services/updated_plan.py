from ..config import settings

from .gemini_client import gemini_service


def generate_updated_plan(
    original_plan,
    feedback,
    goal,
    intensity
):

    if (
        settings.demo_mode
        or not gemini_service.available
    ):

        return (
            original_plan

            + "\n\n"
            + "FITBUDDY UPDATED PLAN\n\n"

            + f"Feedback: {feedback}\n"

            + f"Goal: {goal}\n"

            + f"Intensity: {intensity}\n\n"

            + "Adjustment:\n"

            + "The requested change has been noted. "
            "Keep progression gradual and preserve "
            "a recovery/rest day."
        )


    prompt = f"""
You are FitBuddy.

Revise this 7-day workout plan.

Goal:
{goal}

Intensity:
{intensity}


ORIGINAL PLAN:

{original_plan}


USER FEEDBACK:

{feedback}


Create a complete revised
7-day workout plan.

Apply the feedback.

Keep progression gradual.

Keep at least one recovery/rest day.

Do not diagnose medical conditions.

Do not provide medical treatment.

Return only the revised plan.
"""


    return gemini_service.generate(
        settings.gemini_workout_model,
        prompt,
        4000
    )