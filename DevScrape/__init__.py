"""DevScrape - Hackathon project analyzer and database manager."""
from .config import DB_PATH, GOOGLE_API_KEY, client
from .backend import auto_insert_hack, findTrendswithGemini, analyzeProjectForHackathon
from .database import delete_by_id

__all__ = [
    'DB_PATH',
    'GOOGLE_API_KEY', 
    'client',
    'auto_insert_hack',
    'findTrendswithGemini',
    'analyzeProjectForHackathon',
    'delete_by_id'
]
