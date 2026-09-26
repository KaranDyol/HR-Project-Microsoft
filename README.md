# PeopleOS Workforce Intelligence

A focused AI workforce intelligence MVP built around one defensible flow:

`structured HR data -> deterministic analytics -> Gemini reasoning -> evidence-backed recommendation -> human decision`

## Run locally

```powershell
cd "d:\Projects\HR Project Microsoft\Backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://127.0.0.1:8000. The FastAPI app serves the frontend and API from one process.

## Deploy to Vercel

Import this repository as one Vercel project with the repository root as the project root. Vercel uses the root `index.py` entrypoint for FastAPI, serves the `Frontend/` files through the app, and handles `/api` routes on the same origin. The root `requirements.txt` installs the backend dependencies.

Set `HR_ADMIN_EMAIL` and `HR_ADMIN_PASSWORD` in Vercel project environment variables; they are required to seed the production HR Admin account. Add `GEMINI_API_KEY` to enable Gemini-backed features, and optionally set `GEMINI_MODEL`.

SQLite is initialized from the app's seed data in `/tmp` on Vercel. Vercel function storage is temporary and instance-local, so user changes and accounts are not durable across cold starts or instances. Use a persistent external database before relying on this deployment for real HR data. Do not upload `.env` or database files.

This MVP loads the server-side Gemini variables from the root `.env.example` file. The key is never included in frontend code. Without a configured key, the policy desk remains usable as a clearly marked review-needed state rather than inventing policy answers.

## Current MVP slice

- Workforce dashboard with headcount, recruitment, risk and performance signals
- Deterministic attrition risk heuristic using employee evidence
- SQLite seed database for employees, roles and fictional HR policy excerpts
- Centralized Gemini service boundary for policy reasoning
- Responsive HTML, CSS and JavaScript frontend
