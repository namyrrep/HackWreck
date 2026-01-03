# HackWreck

AI-powered hackathon project analyzer. Uses Google Gemini to evaluate GitHub repos, identify winning trends, and provide strategic recommendations.

## Live Deployments

- **Backend (Railway):** https://hackwreck-production.up.railway.app
	- Health: https://hackwreck-production.up.railway.app/
	- Docs: https://hackwreck-production.up.railway.app/docs

## Quick Start

### Backend
```bash
pip install -r requirements.txt
```

### Frontend
```bash
cd hackwreck-front-end
npm install
```

### Environment Variables
Create a `.env` file in the root directory (used by the backend):
```env
GOOGLE_API_KEY=your_api_key

# Optional (recommended): enable Snowflake instead of local SQLite
USE_SNOWFLAKE=true

SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD="your_password"
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema

# Production CORS (comma-separated). Example:
# CORS_ORIGINS=https://hack-wreck-ecru.vercel.app
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Run
```bash
# Start API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in another terminal)
cd hackwreck-front-end
npm run dev
```

## Deploy

### Backend on Railway

- Deployed from repo root using Nixpacks (`nixpacks.toml`).
- Railway should expose the service (Public Networking) on:
	- https://hackwreck-production.up.railway.app

**Required Railway Variables**
- `GOOGLE_API_KEY`
- `USE_SNOWFLAKE` (set to `true` if using Snowflake)
- Snowflake variables (`SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_SCHEMA`)
- `CORS_ORIGINS` set to your Vercel site origin (exact match), e.g.
	- `CORS_ORIGINS=https://hack-wreck-ecru.vercel.app`

### Frontend on Vercel

- Set the Vercel **Root Directory** to `hackwreck-front-end`.
- Build command: `npm run build`
- Output directory: `dist`

**Required Vercel Env Vars**
- `VITE_API_URL` = `https://hackwreck-production.up.railway.app`

If a friend can't access the Vercel link and it redirects to a Vercel SSO page, disable any deployment protection/authentication so the site is public.

## Features

- **Auto-analyze GitHub repos** - Gemini extracts project details and frameworks
- **AI Scoring** - Projects get a winning potential score (0-10)
- **Trend Analysis** - Find patterns among winning projects
- **Strategic Advice** - Get recommendations based on your project idea

## Tech Stack

| Backend | Frontend |
|---------|----------|
| FastAPI | React |
| Snowflake | TypeScript |
| Google Gemini | Vite |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats` | Database statistics |
| GET | `/api/projects` | All projects |
| POST | `/api/insert` | Add a project |
| POST | `/api/trends` | Get trend analysis |
| POST | `/api/analyze-project` | Analyze project for hackathon |
| DELETE | `/api/projects/{id}` | Delete a project |

## License

MIT
