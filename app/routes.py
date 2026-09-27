from datetime import datetime

from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    Form,
    Header,
    HTTPException,
    Request
)

from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

from sqlalchemy import select

from sqlalchemy.orm import Session

from .config import settings

from .database import get_db

from .models import User, WorkoutPlan

from .schemas import (
    FeedbackRequest,
    UserInput
)

from .services.gemini_generator import (
    generate_workout
)

from .services.gemini_flash_generator import (
    generate_nutrition_tip
)

from .services.updated_plan import (
    generate_updated_plan
)


BASE_DIR = Path(
    __file__
).resolve().parent.parent


templates = Jinja2Templates(
    directory=str(
        BASE_DIR / "templates"
    )
)


router = APIRouter()


def get_user(
    db: Session,
    user_id: str
):

    user = db.scalar(

        select(User).where(
            User.user_id == user_id
        )
    )


    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found."
        )


    return user


def latest_plan(
    db: Session,
    user_id: str
):

    return db.scalar(

        select(WorkoutPlan)

        .where(
            WorkoutPlan.user_id == user_id
        )

        .order_by(
            WorkoutPlan.created_at.desc()
        )
    )


@router.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={}
    )


@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_form(

    request: Request,

    username: str = Form(...),

    user_id: str = Form(...),

    age: int = Form(...),

    weight: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...),

    db: Session = Depends(get_db)
):

    data = UserInput(

        username=username,

        user_id=user_id,

        age=age,

        weight=weight,

        goal=goal,

        intensity=intensity
    )


    user = db.scalar(

        select(User).where(
            User.user_id == data.user_id
        )
    )


    if user:

        user.username = data.username

        user.age = data.age

        user.weight = data.weight

        user.goal = data.goal

        user.intensity = data.intensity

    else:

        user = User(
            **data.model_dump()
        )

        db.add(user)


    workout = generate_workout(

        data.username,

        data.age,

        data.weight,

        data.goal,

        data.intensity
    )


    nutrition_tip = generate_nutrition_tip(
        data.goal
    )


    plan = WorkoutPlan(

        user_id=data.user_id,

        original_plan=workout,

        nutrition_tip=nutrition_tip
    )


    db.add(plan)

    db.commit()

    db.refresh(user)

    db.refresh(plan)


    return templates.TemplateResponse(

        request=request,

        name="result.html",

        context={

            "user": user,

            "plan": plan,

            "active_plan": workout,

            "updated": False
        }
    )


@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def feedback_form(

    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

    db: Session = Depends(get_db)
):

    payload = FeedbackRequest(

        user_id=user_id,

        feedback=feedback
    )


    user = get_user(
        db,
        payload.user_id
    )


    plan = latest_plan(
        db,
        payload.user_id
    )


    if not plan:

        raise HTTPException(
            status_code=404,
            detail="No workout plan exists."
        )


    revised = generate_updated_plan(

        plan.updated_plan
        or plan.original_plan,

        payload.feedback,

        user.goal,

        user.intensity
    )


    plan.updated_plan = revised

    plan.feedback = payload.feedback

    plan.updated_at = datetime.utcnow()


    db.commit()

    db.refresh(plan)


    return templates.TemplateResponse(

        request=request,

        name="result.html",

        context={

            "user": user,

            "plan": plan,

            "active_plan": revised,

            "updated": True
        }
    )


@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def all_users(

    request: Request,

    x_admin_token: str | None = Header(
        default=None
    ),

    db: Session = Depends(get_db)
):

    if (
        settings.admin_token
        and x_admin_token != settings.admin_token
    ):

        raise HTTPException(
            status_code=403,
            detail="Invalid admin token."
        )


    users = db.scalars(

        select(User)

        .order_by(
            User.created_at.desc()
        )
    ).all()


    rows = []


    for user in users:

        rows.append({

            "user": user,

            "plan": latest_plan(
                db,
                user.user_id
            )
        })


    return templates.TemplateResponse(

        request=request,

        name="all_users.html",

        context={
            "rows": rows
        }
    )


@router.get("/health")
def health():

    return {

        "status": "ok",

        "service": "FitBuddy"
    }


@router.post("/api/users")
def create_user(

    payload: UserInput,

    db: Session = Depends(get_db)
):

    existing = db.scalar(

        select(User).where(
            User.user_id == payload.user_id
        )
    )


    if existing:

        raise HTTPException(
            status_code=409,
            detail="User ID already exists."
        )


    user = User(
        **payload.model_dump()
    )


    db.add(user)

    db.commit()

    db.refresh(user)


    return {

        "message": "User created",

        "user_id": user.user_id
    }


@router.post(
    "/api/users/{user_id}/generate"
)
def api_generate(

    user_id: str,

    db: Session = Depends(get_db)
):

    user = get_user(
        db,
        user_id
    )


    workout = generate_workout(

        user.username,

        user.age,

        user.weight,

        user.goal,

        user.intensity
    )


    tip = generate_nutrition_tip(
        user.goal
    )


    plan = WorkoutPlan(

        user_id=user.user_id,

        original_plan=workout,

        nutrition_tip=tip
    )


    db.add(plan)

    db.commit()

    db.refresh(plan)


    return {

        "user_id": user.user_id,

        "plan_id": plan.id,

        "workout_plan": workout,

        "nutrition_tip": tip
    }


@router.post(
    "/api/users/{user_id}/feedback"
)
def api_feedback(

    user_id: str,

    payload: FeedbackRequest,

    db: Session = Depends(get_db)
):

    if payload.user_id != user_id:

        raise HTTPException(

            status_code=400,

            detail=(
                "Path user_id and payload "
                "user_id must match."
            )
        )


    user = get_user(
        db,
        user_id
    )


    plan = latest_plan(
        db,
        user_id
    )


    if not plan:

        raise HTTPException(

            status_code=404,

            detail="No workout plan exists."
        )


    revised = generate_updated_plan(

        plan.updated_plan
        or plan.original_plan,

        payload.feedback,

        user.goal,

        user.intensity
    )


    plan.updated_plan = revised

    plan.feedback = payload.feedback

    plan.updated_at = datetime.utcnow()


    db.commit()


    return {

        "user_id": user_id,

        "plan_id": plan.id,

        "updated_plan": revised
    }


@router.get("/api/users")
def list_users(
    db: Session = Depends(get_db)
):

    users = db.scalars(

        select(User)

        .order_by(
            User.created_at.desc()
        )
    ).all()


    return [

        {

            "user_id": user.user_id,

            "username": user.username,

            "age": user.age,

            "weight": user.weight,

            "goal": user.goal,

            "intensity": user.intensity,

            "created_at":
                user.created_at.isoformat()
        }

        for user in users
    ]


@router.get(
    "/api/users/{user_id}"
)
def user_api(

    user_id: str,

    db: Session = Depends(get_db)
):

    user = get_user(
        db,
        user_id
    )


    plan = latest_plan(
        db,
        user_id
    )


    return {

        "user": {

            "user_id": user.user_id,

            "username": user.username,

            "age": user.age,

            "weight": user.weight,

            "goal": user.goal,

            "intensity": user.intensity
        },


        "plan":

        None

        if not plan

        else {

            "id": plan.id,

            "original_plan":
                plan.original_plan,

            "updated_plan":
                plan.updated_plan,

            "nutrition_tip":
                plan.nutrition_tip,

            "feedback":
                plan.feedback
        }
    }