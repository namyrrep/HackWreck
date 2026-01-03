"""
Database module - Snowflake connection.

Usage:
    from DevScrape.db import (
        check_duplicate_project,
        insert_project,
        delete_by_id,
        get_winners_by_category,
        # ... etc
    )
"""
from .database_snowflake import (
    check_duplicate_project,
    insert_project,
    delete_by_id,
    get_winners_by_category,
    get_winners_excluding_category,
    get_participants,
    get_winners_by_framework,
    get_top_winners,
    get_database_stats
)

__all__ = [
    'check_duplicate_project',
    'insert_project',
    'delete_by_id',
    'get_winners_by_category',
    'get_winners_excluding_category',
    'get_participants',
    'get_winners_by_framework',
    'get_top_winners',
    'get_database_stats'
]
