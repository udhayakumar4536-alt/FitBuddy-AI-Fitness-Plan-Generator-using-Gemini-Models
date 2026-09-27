from ..config import settings

from .gemini_client import gemini_service


def demo_workout(
    username,
    goal,
    intensity
):

    return f"""
FITBUDDY 7-DAY WORKOUT PLAN

User: {username}

Goal: {goal.title()}

Intensity: {intensity.title()}


DAY 1 - FULL BODY

Warm-up:
8 minutes walking and mobility.

Squats - 3 x 10

Push-ups - 3 x 8-12

Rows - 3 x 10

Glute bridges - 3 x 12

Cooldown:
5 minutes.


DAY 2 - CARDIO + CORE

Brisk walking or cycling:
25 minutes

Plank:
3 x 30 seconds

Dead bug:
3 x 10 per side


DAY 3 - RECOVERY

Easy walking:
20-30 minutes

Gentle stretching.


DAY 4 - UPPER BODY + CORE

Incline push-ups:
3 x 10

Rows:
3 x 10

Shoulder press:
3 x 10

Bird-dog:
3 x 10 per side


DAY 5 - LOWER BODY

Squats:
3 x 10

Reverse lunges:
3 x 8 per leg

Hip hinge:
3 x 10

Calf raises:
3 x 15


DAY 6 - CARDIO + FLEXIBILITY

Moderate cardio:
25-30 minutes

Full body mobility:
10 minutes


DAY 7 - REST

Rest and recovery.


SAFETY

Use controlled technique.

Stop if you experience sharp
or unusual pain.

Adjust exercises according to
your comfort and experience.
"""


def generate_workout(
    username,
    age,
    weight,
    goal,
    intensity
):

    if (
        settings.demo_mode
        or not gemini_service.available
    ):

        return demo_workout(
            username,
            goal,
            intensity
        )


    prompt = f"""
You are FitBuddy.

Create a personalized 7-day workout plan.

USER:

Name: {username}

Age: {age}

Weight: {weight} kg

Goal: {goal}

Intensity: {intensity}


Requirements:

- Exactly 7 labeled days.
- Include warm-up.
- Include exercises.
- Include sets/repetitions or duration.
- Include recovery.
- Include cooldown.
- Include at least one rest day.
- Add a short safety note.
- Do not diagnose medical conditions.
- Do not prescribe supplements.
- Avoid extreme exercise.

Return only the workout plan.
"""


    return gemini_service.generate(
        settings.gemini_workout_model,
        prompt,
        3500
    )