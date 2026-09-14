# T-001: Project Scaffolding & Environment Setup

* **Status**: DONE
* **Responsible Agent**: Architect Agent
* **Dependencies**: None

## Goal
Establish backend and frontend project boilerplates, dependency definitions, and development scripts.

## Deliverables
1. Backend (`backend/`):
   - Virtual environment (`backend/.venv`) created.
   - `backend/requirements.txt` containing FastAPI, Uvicorn, Pydantic, pdfplumber, google-genai, pytest, httpx, reportlab.
   - `backend/app/main.py` with `/health` endpoint and CORS middleware.
   - `backend/app/core/config.py` with environment configuration.
   - `backend/.env.example` with standard environment variables.
   - `backend/tests/test_health.py` and `backend/pytest.ini` passing with 100% success.
2. Frontend (`frontend/`):
   - React 18 + TypeScript + Vite + Tailwind CSS initialized.
   - Clean starter dashboard in `frontend/src/App.tsx`.
   - `npm run build` succeeds cleanly.

## Verification
- Backend test: `pytest` passed (1 passed in 0.65s).
- Frontend test: `npm run build` succeeded without errors.
- Secrets: No API keys or secrets committed.
