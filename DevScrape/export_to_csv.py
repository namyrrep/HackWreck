"""Export SQLite data to CSV for Snowflake migration."""
import sqlite3
import csv
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DevScrape.config import DB_PATH

def export_to_csv():
    """Export hacks table to CSV."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM hacks")
    rows = cursor.fetchall()
    
    # Get column names
    cursor.execute("PRAGMA table_info(hacks)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Write to CSV
    output_file = os.path.join(os.path.dirname(DB_PATH), 'hacks_export.csv')
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    
    conn.close()
    print(f"Exported {len(rows)} rows to {output_file}")
    return output_file

if __name__ == "__main__":
    export_to_csv()
