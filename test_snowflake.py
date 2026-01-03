"""Test Snowflake connection."""
from DevScrape.config import SNOWFLAKE_CONFIG

print("SNOWFLAKE_CONFIG:")
for k, v in SNOWFLAKE_CONFIG.items():
    if k == 'password':
        print(f"  {k}: ****")
    else:
        print(f"  {k}: {v}")

from DevScrape.db import get_database_stats

try:
    stats = get_database_stats()
    print("\n✓ Snowflake connection successful!")
    print(f"  Total projects: {stats['total_projects']}")
    print(f"  Total winners: {stats['total_winners']}")
    print(f"  Avg winner score: {stats['avg_winner_score']:.1f}")
except Exception as e:
    print(f"\n✗ Connection failed: {e}")
