from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn
import sys
import os

# Import from DevScrape package
from DevScrape import (
    auto_insert_hack, 
    findTrendswithGemini, 
    wreckMeWithGemini,
    analyzeProjectForHackathon, 
    delete_by_id, 
    client, 
    GOOGLE_API_KEY,
    get_database_stats,
    get_snowflake_connection
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup checks
    print("\n" + "="*50)
    print("HackWreck API Starting...")
    print("="*50)
    
    # Check 1: Snowflake Database
    try:
        with get_snowflake_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM HACKS")
            count = cursor.fetchone()[0]
        print(f"[OK] Snowflake Database: Connected ({count} projects)")
    except Exception as e:
        print(f"[ERROR] Snowflake Database: {e}")
    
    # Check 2: API Key
    if GOOGLE_API_KEY:
        print(f"[OK] API Key: Configured ({GOOGLE_API_KEY[:3]}...)")
    else:
        print("[ERROR] API Key: Missing - set GOOGLE_API_KEY in .env")
    
    # Check 3: Gemini API connection
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Reply with only: OK"
        )
        if response.text:
            print("[OK] Gemini API: Connected")
    except Exception as e:
        print(f"[ERROR] Gemini API: {e}")
    
    print("="*50)
    print("API Docs: http://localhost:8000/docs")
    print("="*50 + "\n")
    
    yield  # Server runs here
    
    # Shutdown
    print("\nHackWreck API shutting down...")


app = FastAPI(
    title="HackWreck API", 
    description="AI-powered hackathon trend analysis",
    lifespan=lifespan
)

def _parse_cors_origins(value: str | None) -> list[str]:
    if not value:
        return ["http://localhost:3000", "http://localhost:5173"]
    value = value.strip()
    if value == "*":
        return ["*"]
    origins: list[str] = []
    for origin in value.split(","):
        normalized = origin.strip()
        if not normalized:
            continue
        # Origins are compared as exact strings by the CORS middleware.
        # Users sometimes paste values with a trailing slash; strip it.
        normalized = normalized.rstrip("/")
        origins.append(normalized)
    return origins


# CORS for frontend (configurable in production)
_cors_origins = _parse_cors_origins(os.getenv("CORS_ORIGINS"))
_cors_allows_any = "*" in _cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=not _cors_allows_any,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class InsertRequest(BaseModel):
    github_url: str
    status: str  # 'winner' or 'participant'


class InsertResponse(BaseModel):
    success: bool
    message: str
    project_name: str | None = None


class TrendRequest(BaseModel):
    category: str
    framework: str
    description: str


class TrendResponse(BaseModel):
    success: bool
    analysis: str


class WreckMeResponse(BaseModel):
    success: bool
    analysis: str


class ProjectAnalysisRequest(BaseModel):
    github_url: str
    hackathon_name: str
    hackathon_theme: str = ""


class ProjectAnalysisResponse(BaseModel):
    success: bool
    project_analysis: dict
    suggestions: str
    related_winners: list
    hackathon_name: str
    hackathon_theme: str


class ProjectResponse(BaseModel):
    id: int
    name: str
    framework: str | None
    githubLink: str | None
    place: str | None
    topic: str | None
    descriptions: str | None
    ai_score: float | None
    ai_reasoning: str | None


# Endpoints
@app.get("/")
async def root():
    return {"message": "HackWreck API is running", "docs": "/docs"}


@app.post("/api/insert", response_model=InsertResponse)
async def insert_project(request: InsertRequest):
    """
    Analyze a GitHub repository and insert it into the database.
    Gemini will extract project details and assign an AI score.
    """
    try:
        result = auto_insert_hack(request.github_url, request.status)
        if result:
            return InsertResponse(
                success=True,
                message="Project successfully added",
                project_name=None  # Would need to modify auto_insert_hack to return the name
            )
        else:
            return InsertResponse(
                success=False,
                message="Duplicate project - already exists in database"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/trends", response_model=TrendResponse)
async def get_trends(request: TrendRequest):
    """
    Get AI-powered trend analysis and advice for your hackathon project idea.
    """
    try:
        analysis = findTrendswithGemini(
            request.category,
            request.framework,
            request.description
        )
        return TrendResponse(success=True, analysis=analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/wreck-me", response_model=WreckMeResponse)
async def wreck_me():
    """Generate a random, polished hackathon idea pitch (Markdown) via Gemini."""
    try:
        analysis = wreckMeWithGemini()
        return WreckMeResponse(success=True, analysis=analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-project", response_model=ProjectAnalysisResponse)
async def analyze_project_for_hackathon(request: ProjectAnalysisRequest):
    """
    Analyze an existing GitHub project and provide improvement suggestions
    for a specific hackathon based on previous winners.
    """
    try:
        result = analyzeProjectForHackathon(
            request.github_url,
            request.hackathon_name,
            request.hackathon_theme
        )
        return ProjectAnalysisResponse(
            success=True,
            project_analysis=result["project_analysis"],
            suggestions=result["suggestions"],
            related_winners=result["related_winners"],
            hackathon_name=result["hackathon_name"],
            hackathon_theme=result["hackathon_theme"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects", response_model=list[ProjectResponse])
async def get_all_projects():
    """
    Get all projects from the database.
    """
    with get_snowflake_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, framework, githubLink, place, topic, descriptions, ai_score, ai_reasoning FROM HACKS")
        rows = cursor.fetchall()
    
    columns = ['id', 'name', 'framework', 'githubLink', 'place', 'topic', 'descriptions', 'ai_score', 'ai_reasoning']
    return [ProjectResponse(**dict(zip(columns, row))) for row in rows]


@app.get("/api/projects/winners", response_model=list[ProjectResponse])
async def get_winners():
    """
    Get all winning projects from the database.
    """
    with get_snowflake_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, framework, githubLink, place, topic, descriptions, ai_score, ai_reasoning FROM HACKS WHERE LOWER(place) LIKE '%winner%'")
        rows = cursor.fetchall()
    
    columns = ['id', 'name', 'framework', 'githubLink', 'place', 'topic', 'descriptions', 'ai_score', 'ai_reasoning']
    return [ProjectResponse(**dict(zip(columns, row))) for row in rows]


@app.get("/api/stats")
async def get_stats():
    """
    Get database statistics.
    """
    stats = get_database_stats()
    
    return {
        "total_projects": stats["total_projects"],
        "total_winners": stats["total_winners"],
        "total_participants": stats["total_projects"] - stats["total_winners"],
        "avg_winner_score": round(stats["avg_winner_score"], 1),
        "top_frameworks": [{"framework": fw, "count": cnt} for fw, cnt in stats["top_frameworks"]],
        "top_categories": [{"category": cat, "count": cnt} for cat, cnt in stats["top_categories"]]
    }


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: int):
    """
    Delete a project by ID from the database.
    """
    result = delete_by_id(project_id)
    
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
