# Tech-Law RAG Backend

Backend FastAPI for the Tech-Law RAG project.

## Run locally

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/health
```

## Run tests

```powershell
cd backend
python -m pytest
```
