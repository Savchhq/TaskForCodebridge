# T-001: Project Scaffolding & Environment Setup

* **Status**: IN_PROGRESS
* **Responsible Agent**: Architect Agent
* **Dependencies**: None

## Goal
Establish backend and frontend project boilerplates, dependency definitions, and development scripts.

## Requirements
1. Backend (`backend/`):
   - Python virtual environment instructions and `requirements.txt` containing FastAPI, Uvicorn, Pydantic, pdfplumber, python-dotenv, google-genai, pytest, httpx.
   - Minimal runnable FastAPI app (`backend/app/main.py`) with a `GET /health` endpoint.
   - `.env.example` defining `GEMINI_API_KEY`, `PORT`, etc.
2. Frontend (`frontend/`):
   - React + TypeScript + Vite project initialized with Tailwind CSS.
   - Clean starter page displaying project title and API health check status.
3. Verification:
   - Backend health endpoint returns `{"status": "ok"}`.
   - Frontend builds cleanly via `npm run build`.

## Acceptance Criteria
- [ ] Backend runs with `uvicorn app.main:app` and answers `/health`.
- [ ] Frontend builds without TypeScript or bundling errors.
- [ ] No secrets committed.
