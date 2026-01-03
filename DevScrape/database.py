"""Database operations for hackathon projects."""
import sqlite3
from .config import DB_PATH


def check_duplicate_project(github_url):
    """
    Check if a project with the given GitHub URL already exists.
    
    Args:
        github_url: GitHub repository URL to check
        
    Returns:
        tuple: (exists: bool, project_id: int, project_name: str) or (False, None, None)
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name FROM hacks WHERE githubLink = ?", (github_url,))
    existing = c.fetchone()
    conn.close()
    
    if existing:
        return True, existing[0], existing[1]
    return False, None, None


def insert_project(name, framework, github_url, status, topic, descriptions, ai_score, ai_reasoning):
    """
    Insert a new project into the database.
    
    Args:
        name: Project name
        framework: Primary framework/languages used
        github_url: GitHub repository URL
        status: Winner or participant status
        topic: Category (AI, FinTech, etc.)
        descriptions: Project summary
        ai_score: AI rating (0.0-10.0)
        ai_reasoning: Explanation for the score
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO hacks (name, framework, githubLink, place, topic, descriptions, ai_score, ai_reasoning)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, framework, github_url, status, topic, descriptions, ai_score, ai_reasoning))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def delete_by_id(project_id):
    """
    Delete a project from the database by its ID.
    
    Args:
        project_id: The ID of the project to delete
        
    Returns:
        dict: {"success": bool, "message": str, "project_name": str or None}
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if project exists
    c.execute("SELECT id, name FROM hacks WHERE id = ?", (project_id,))
    project = c.fetchone()
    
    if not project:
        conn.close()
        return {
            "success": False,
            "message": f"Project with ID {project_id} not found",
            "project_name": None
        }
    
    project_name = project[1]
    
    # Delete the project
    c.execute("DELETE FROM hacks WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "message": f"Successfully deleted project '{project_name}' (ID: {project_id})",
        "project_name": project_name
    }


def get_winners_by_category(category, limit=10):
    """
    Fetch winning projects in a specific category.
    
    Args:
        category: The category/topic to search for
        limit: Maximum number of results
        
    Returns:
        list: List of tuples containing project data
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT name, framework, topic, descriptions, ai_score, ai_reasoning 
        FROM hacks 
        WHERE LOWER(place) LIKE '%winner%' AND LOWER(topic) LIKE ? 
        ORDER BY ai_score DESC 
        LIMIT ?
    """, (f'%{category.lower()}%', limit))
    results = c.fetchall()
    conn.close()
    return results


def get_winners_excluding_category(category, limit=10):
    """
    Fetch winning projects excluding a specific category.
    
    Args:
        category: The category/topic to exclude
        limit: Maximum number of results
        
    Returns:
        list: List of tuples containing project data
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT name, framework, topic, descriptions, ai_score, ai_reasoning 
        FROM hacks 
        WHERE LOWER(place) LIKE '%winner%' AND LOWER(topic) NOT LIKE ?
        ORDER BY ai_score DESC 
        LIMIT ?
    """, (f'%{category.lower()}%', limit))
    results = c.fetchall()
    conn.close()
    return results


def get_participants(limit=5):
    """
    Fetch non-winning (participant) projects.
    
    Args:
        limit: Maximum number of results
        
    Returns:
        list: List of tuples containing project data
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT name, framework, topic, descriptions, ai_score, ai_reasoning 
        FROM hacks 
        WHERE LOWER(place) NOT LIKE '%winner%'
        ORDER BY ai_score DESC 
        LIMIT ?
    """, (limit,))
    results = c.fetchall()
    conn.close()
    return results


def get_winners_by_framework(framework, limit=5):
    """
    Get winners using a similar framework.
    
    Args:
        framework: Framework/technology to search for
        limit: Maximum number of results
        
    Returns:
        list: List of tuples containing project data
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Extract first framework/tech from comma/slash separated list
    framework_key = framework.split(",")[0].split("/")[0].strip()
    c.execute("""
        SELECT name, framework, topic, descriptions, ai_score, ai_reasoning 
        FROM hacks 
        WHERE LOWER(place) LIKE '%winner%' 
        AND LOWER(framework) LIKE ?
        ORDER BY ai_score DESC 
        LIMIT ?
    """, (f'%{framework_key.lower()}%', limit))
    results = c.fetchall()
    conn.close()
    return results


def get_top_winners(limit=5):
    """
    Get top winning projects overall.
    
    Args:
        limit: Maximum number of results
        
    Returns:
        list: List of tuples containing project data
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT name, framework, topic, descriptions, ai_score, ai_reasoning 
        FROM hacks 
        WHERE LOWER(place) LIKE '%winner%'
        ORDER BY ai_score DESC 
        LIMIT ?
    """, (limit,))
    results = c.fetchall()
    conn.close()
    return results


def get_database_stats():
    """
    Get aggregate statistics from the database.
    
    Returns:
        dict: Statistics including counts, averages, and top frameworks/categories
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM hacks WHERE LOWER(place) LIKE '%winner%'")
    total_winners = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM hacks")
    total_projects = c.fetchone()[0]
    
    c.execute("""
        SELECT framework, COUNT(*) as cnt 
        FROM hacks 
        WHERE LOWER(place) LIKE '%winner%' 
        GROUP BY framework 
        ORDER BY cnt DESC 
        LIMIT 5
    """)
    top_frameworks = c.fetchall()
    
    c.execute("""
        SELECT topic, COUNT(*) as cnt 
        FROM hacks 
        WHERE LOWER(place) LIKE '%winner%' 
        GROUP BY topic 
        ORDER BY cnt DESC 
        LIMIT 5
    """)
    top_categories = c.fetchall()
    
    c.execute("SELECT AVG(ai_score) FROM hacks WHERE LOWER(place) LIKE '%winner%'")
    avg_winner_score = c.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "total_projects": total_projects,
        "total_winners": total_winners,
        "avg_winner_score": avg_winner_score,
        "top_frameworks": top_frameworks,
        "top_categories": top_categories
    }
