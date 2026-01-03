"""Snowflake database operations for hackathon projects."""
import snowflake.connector
from contextlib import contextmanager
from .config import SNOWFLAKE_CONFIG


@contextmanager
def get_snowflake_connection():
    """Context manager for Snowflake connections."""
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    try:
        yield conn
    finally:
        conn.close()


def check_duplicate_project(github_url):
    """Check if a project with the given GitHub URL already exists."""
    with get_snowflake_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM HACKS WHERE githubLink = %s", (github_url,))
        existing = cursor.fetchone()
        
        if existing:
            return True, existing[0], existing[1]
        return False, None, None


def insert_project(name, framework, github_url, status, topic, descriptions, ai_score, ai_reasoning):
    """Insert a new project into the database."""
    try:
        with get_snowflake_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO HACKS (name, framework, githubLink, place, topic, descriptions, ai_score, ai_reasoning)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (name, framework, github_url, status, topic, descriptions, ai_score, ai_reasoning))
            conn.commit()
            return True
    except Exception as e:
        print(f"Database error: {e}")
        return False


def delete_by_id(project_id):
    """Delete a project from the database by its ID."""
    with get_snowflake_connection() as conn:
        cursor = conn.cursor()
        
        # Check if project exists
        cursor.execute("SELECT id, name FROM HACKS WHERE id = %s", (project_id,))
        project = cursor.fetchone()
        
        if not project:
            return {
                "success": False,
                "message": f"Project with ID {project_id} not found",
                "project_name": None
            }
        
        project_name = project[1]
        
        # Delete the project
        cursor.execute("DELETE FROM HACKS WHERE id = %s", (project_id,))
        conn.commit()
        
        return {
            "success": True,
            "message": f"Successfully deleted project '{project_name}' (ID: {project_id})",
            "project_name": project_name
        }


def get_winners_by_category(category, limit=10):
    """Fetch winning projects in a specific category."""
    with get_snowflake_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, framework, topic, descriptions, ai_score, ai_reasoning, githubLink 
            FROM HACKS 
            WHERE LOWER(place) LIKE %s AND LOWER(topic) LIKE %s
            ORDER BY ai_score DESC 
            LIMIT %s
        """, ('%winner%', f'%{category.lower()}%', limit))
        return cursor.fetchall()


def get_winners_excluding_category(category, limit=10):
    """Fetch winning projects excluding a specific category."""
    with get_snowflake_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, framework, topic, descriptions, ai_score, ai_reasoning 
            FROM HACKS 
            WHERE LOWER(place) LIKE %s AND LOWER(topic) NOT LIKE %s
            ORDER BY ai_score DESC 
            LIMIT %s
        """, ('%winner%', f'%{category.lower()}%', limit))
        return cursor.fetchall()


def get_participants(limit=5):
    """Fetch non-winning (participant) projects."""
    with get_snowflake_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, framework, topic, descriptions, ai_score, ai_reasoning 
            FROM HACKS 
            WHERE LOWER(place) NOT LIKE %s
            ORDER BY ai_score DESC 
            LIMIT %s
        """, ('%winner%', limit))
        return cursor.fetchall()


def get_winners_by_framework(framework, limit=5):
    """Get winners using a similar framework."""
    framework_key = framework.split(",")[0].split("/")[0].strip()
    
    with get_snowflake_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, framework, topic, descriptions, ai_score, ai_reasoning, githubLink 
            FROM HACKS 
            WHERE LOWER(place) LIKE %s 
            AND LOWER(framework) LIKE %s
            ORDER BY ai_score DESC 
            LIMIT %s
        """, ('%winner%', f'%{framework_key.lower()}%', limit))
        return cursor.fetchall()


def get_top_winners(limit=5):
    """Get top winning projects overall."""
    with get_snowflake_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, framework, topic, descriptions, ai_score, ai_reasoning, githubLink 
            FROM HACKS 
            WHERE LOWER(place) LIKE %s
            ORDER BY ai_score DESC 
            LIMIT %s
        """, ('%winner%', limit))
        return cursor.fetchall()


def get_database_stats():
    """Get aggregate statistics from the database."""
    with get_snowflake_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM HACKS WHERE LOWER(place) LIKE '%winner%'")
        total_winners = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM HACKS")
        total_projects = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT framework, COUNT(*) as cnt 
            FROM HACKS 
            WHERE LOWER(place) LIKE '%winner%' 
            GROUP BY framework 
            ORDER BY cnt DESC 
            LIMIT 5
        """)
        top_frameworks = cursor.fetchall()
        
        cursor.execute("""
            SELECT topic, COUNT(*) as cnt 
            FROM HACKS 
            WHERE LOWER(place) LIKE '%winner%' 
            GROUP BY topic 
            ORDER BY cnt DESC 
            LIMIT 5
        """)
        top_categories = cursor.fetchall()
        
        cursor.execute("SELECT AVG(ai_score) FROM HACKS WHERE LOWER(place) LIKE '%winner%'")
        avg_winner_score = cursor.fetchone()[0] or 0
        
        return {
            "total_projects": total_projects,
            "total_winners": total_winners,
            "avg_winner_score": avg_winner_score,
            "top_frameworks": top_frameworks,
            "top_categories": top_categories
        }
