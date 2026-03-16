# Deployment Guide

## Overview

The application is split into two independently deployable units:
- **Frontend**: Static site → Vercel (or Netlify, Cloudflare Pages)
- **Backend**: Python API → Railway, Render, or Fly.io

---

## Frontend Deployment (Vercel)

### 1. Build

```bash
cd frontend
npm run build
# Output: dist/
```

### 2. Deploy to Vercel

```bash
npm install -g vercel
vercel login
vercel --prod
```

Or connect GitHub repo in Vercel dashboard:
- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`

### 3. Environment Variables (Vercel Dashboard)

```
VITE_API_URL=https://your-backend.railway.app
VITE_APP_TITLE=Chess AI Portfolio
```

---

## Backend Deployment (Railway)

### 1. Prepare

Ensure `backend/Dockerfile` and `backend/requirements.txt` are up to date.

### 2. Deploy

```bash
# Install Railway CLI
npm install -g @railway/cli
railway login
railway init
railway up
```

Or connect GitHub repo in Railway dashboard:
- Root directory: `backend`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. Environment Variables (Railway Dashboard)

```
DATABASE_URL=postgresql://...   # Railway provisions this automatically
ANTHROPIC_API_KEY=sk-ant-...
SECRET_KEY=<random-64-char-string>
CORS_ORIGINS=https://your-frontend.vercel.app
ENVIRONMENT=production
CLAUDE_MODEL=claude-opus-4-6
MODEL_CHECKPOINT_PATH=/app/data/models/value_net.pt
```

### 4. Database Migration

After first deploy:
```bash
railway run alembic upgrade head
```

---

## Backend Deployment (Render)

### 1. Create Web Service

In Render dashboard:
- Repository: your GitHub repo
- Root directory: `backend`
- Runtime: Docker
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2. Add PostgreSQL

Add a PostgreSQL database in Render and copy the `DATABASE_URL`.

### 3. Environment Variables

Same as Railway above.

---

## Backend Deployment (Fly.io)

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login and launch from backend directory
cd backend
fly launch
fly secrets set ANTHROPIC_API_KEY=sk-ant-...
fly secrets set DATABASE_URL=postgresql://...
fly deploy
```

---

## Production Checklist

### Security
- [ ] `SECRET_KEY` is a random 64+ character string
- [ ] `DEBUG=false` in production
- [ ] `CORS_ORIGINS` is set to exact frontend URL (no wildcards)
- [ ] `ANTHROPIC_API_KEY` is in secrets, not in code
- [ ] Database credentials not hardcoded anywhere
- [ ] HTTPS enforced (Vercel/Railway handle this automatically)

### Database
- [ ] Run `alembic upgrade head` after each deploy
- [ ] Database backups configured (Railway/Render offer automatic backups)
- [ ] Connection pool size tuned for serverless environment

### Performance
- [ ] Frontend assets are minified and compressed (`npm run build` handles this)
- [ ] Static assets cached with appropriate headers
- [ ] API response caching for expensive operations (evaluation)
- [ ] Engine timeout set appropriately (`ENGINE_TIMEOUT_SECONDS`)

### Monitoring
- [ ] Application logs accessible (Railway/Render provide log streaming)
- [ ] Error tracking configured (e.g., Sentry)
- [ ] Health check endpoint responding (`/health`)

### ML Model
- [ ] `value_net.pt` checkpoint uploaded to persistent storage
- [ ] `MODEL_CHECKPOINT_PATH` points to correct location
- [ ] Model loads on startup (check `/health/detailed` endpoint)

---

## Environment: Production vs Development

| Setting | Development | Production |
|---------|-------------|------------|
| `DATABASE_URL` | `sqlite:///./chess.db` | PostgreSQL URL |
| `DEBUG` | `true` | `false` |
| `CORS_ORIGINS` | `localhost:5173` | Exact domain |
| `ENVIRONMENT` | `development` | `production` |
| `DEVICE` | `cpu` | `cpu` or `cuda` |

---

## CI/CD Pipeline

The `.github/workflows/ci.yml` pipeline:
1. Runs on every push and pull request
2. Lints and type-checks Python code
3. Runs backend test suite
4. Lints and type-checks TypeScript
5. Builds frontend
6. (Optional) Deploys on merge to `main`

To enable auto-deploy, add these secrets to GitHub:
- `RAILWAY_TOKEN` — for Railway deployment
- `VERCEL_TOKEN` — for Vercel deployment

---

## Scaling Notes

### Stateless Design
The API is designed to be stateless — game state is represented as FEN strings in each request. This enables:
- Horizontal scaling (multiple backend instances)
- No sticky sessions required
- Simple load balancing

### Database Connection Pooling
For high-traffic scenarios, configure connection pooling:
```python
# backend/app/db/session.py
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)
```

### Engine Performance
- Easy/Medium: Completes in < 100ms
- Hard: May take 1–5 seconds for depth 6 search
- Consider background tasks (FastAPI BackgroundTasks) for Hard mode if latency is an issue

### PyTorch Model
- Model is loaded once at startup and cached in memory
- Inference is fast (< 10ms per position)
- For GPU inference, set `DEVICE=cuda` (requires CUDA-enabled host)
