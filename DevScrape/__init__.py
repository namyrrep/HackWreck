"""DevScrape - Hackathon project analyzer and database manager."""
from .config import DB_PATH, GOOGLE_API_KEY, client
from .backend import auto_insert_hack, findTrendswithGemini, analyzeProjectForHackathon, wreckMeWithGemini
from .db import delete_by_id, get_database_stats
from .database_snowflake import get_snowflake_connection

__all__ = [
    'DB_PATH',
    'GOOGLE_API_KEY', 
    'client',
    'auto_insert_hack',
    'findTrendswithGemini',
    'wreckMeWithGemini',
    'analyzeProjectForHackathon',
    'delete_by_id',
    'get_database_stats',
    'get_snowflake_connection'
]
