# HackWreck

AI-powered hackathon project analyzer. Uses Google Gemini to evaluate GitHub repos, identify winning trends, and provide strategic recommendations.

## Quick Start

### Backend
```bash
pip install google-genai python-dotenv fastapi uvicorn snowflake-connector-python
```

### Frontend
```bash
cd hackwreck-front-end
npm install
```

### Environment Variables
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_api_key
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD="your_password"
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
```

### Run
```bash
# Start API server
python main.py

# Start frontend (in another terminal)
cd hackwreck-front-end
npm run dev
```

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
