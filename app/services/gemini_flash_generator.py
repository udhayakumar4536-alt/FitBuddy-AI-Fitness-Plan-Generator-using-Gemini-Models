from ..config import settings

from .gemini_client import gemini_service


DEMO_TIPS = {

    "weight loss":
        "Build meals around vegetables, "
        "a protein source, high-fiber carbohydrates "
        "and water. Consistency matters more than "
        "extreme restriction.",


    "muscle gain":
        "Include a protein-rich food in each main meal "
        "and support training with adequate sleep.",


    "general wellness":
        "Prioritize balanced meals, regular hydration, "
        "fruits, vegetables and consistent sleep.",


    "flexibility":
        "Stay hydrated and include varied whole foods "
        "while practicing gentle mobility consistently."
}


def generate_nutrition_tip(goal):

    if (
        settings.demo_mode
        or not gemini_service.available
    ):

        return DEMO_TIPS.get(
            goal,
            DEMO_TIPS["general wellness"]
        )


    prompt = f"""
Give one concise practical
nutrition or recovery tip.

Fitness goal:
{goal}

Requirements:

2-4 sentences.

Easy to understand.

No medical claims.

No extreme dieting.

Do not prescribe supplements.

Return only the tip.
"""


    return gemini_service.generate(
        settings.gemini_fast_model,
        prompt,
        500
    )