# PeopleOS Backend

FastAPI service for the workforce intelligence MVP.

## Run

```powershell
cd Backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload
```

The API and dashboard are available at http://127.0.0.1:8000.

Set `GEMINI_API_KEY` in the repository `.env` to enable policy reasoning. The key is read only by the backend and is never sent to the browser. Without it, the UI still runs and clearly reports that AI analysis is unavailable.
