# GitHub Pages Deployment Guide

This project is configured to deploy the frontend to GitHub Pages automatically.

## Prerequisites

1. Enable GitHub Pages in your repository settings:
   - Go to Settings → Pages
   - Source: GitHub Actions

2. Set up backend API URL (optional):
   - Go to Settings → Secrets and variables → Actions
   - Add a secret named `VITE_API_BASE_URL` with your backend API URL
   - If not set, it defaults to `http://localhost:8000`

## How It Works

- The GitHub Actions workflow (`.github/workflows/deploy.yml`) automatically:
  1. Builds the frontend when you push to `main`
  2. Deploys it to GitHub Pages
  3. Sets the correct base path (`/repository-name/`)

## Backend Deployment

**Important:** GitHub Pages only hosts static files. You need to deploy the backend separately:

### Option 1: Heroku
```bash
cd backend
heroku create your-app-name
git subtree push --prefix backend heroku main
```

### Option 2: Railway
1. Connect your GitHub repository
2. Set root directory to `backend`
3. Railway will auto-detect FastAPI

### Option 3: Render
1. Create a new Web Service
2. Connect your GitHub repository
3. Set root directory to `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## After Backend Deployment

1. Update the `VITE_API_BASE_URL` secret in GitHub Actions with your backend URL
2. Re-run the deployment workflow or push a new commit

## Local Development

1. Start backend: `cd backend && source venv/bin/activate && python main.py`
2. Start frontend: `cd frontend && npm run dev`
3. Frontend will be available at `http://localhost:3001`

## Production URLs

- Frontend: `https://your-username.github.io/ai-agent-layman-query-engine/`
- Backend: Your deployed backend URL (e.g., `https://your-app.herokuapp.com`)

