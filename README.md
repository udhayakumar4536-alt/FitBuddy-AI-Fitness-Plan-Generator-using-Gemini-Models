# FitBuddy

AI-powered 7-day fitness planner.

## Setup

Create virtual environment:

python -m venv venv

Activate:

venv\Scripts\activate

Install:

pip install -r requirements.txt

Run:

python -m uvicorn app.main:app --reload

Open:

http://127.0.0.1:8000

API Docs:

http://127.0.0.1:8000/docs

Admin:

http://127.0.0.1:8000/view-all-users

## Gemini

Initially the project uses:

DEMO_MODE=true

After the application works, add your Gemini API key to .env and change:

DEMO_MODE=false