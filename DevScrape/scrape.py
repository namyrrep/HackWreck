import sqlite3
import json
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, 'hackathons.db')

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)

def auto_insert_hack(github_url, status):
    # Check for duplicate link first
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name FROM hacks WHERE githubLink = ?", (github_url,))
    existing = c.fetchone()
    if existing:
        conn.close()
        print(f"⚠️  Duplicate detected: '{existing[1]}' already exists with this GitHub link (ID: {existing[0]})")
        return False
    conn.close()
    
    # 1. Ask Gemini to analyze the GitHub link
    prompt = f"""
    Analyze this GitHub repository: {github_url}. 
    The project was a '{status}' in a hackathon.
    Extract the following information and return it ONLY as a JSON object:
    {{
        "name": "Project Name",
        "framework": "Primary Framework/Languages",
        "topic": "Category like AI, FinTech, etc.",
        "descriptions": "A 2-sentence summary of what it does",
        "ai_score": 0.0,
        "ai_reasoning": "Explanation for the score"
    }}
    
    For ai_score, rate the project's "winning potential" from 0.0 to 10.0 based on:
    - Innovation and creativity
    - Technical complexity
    - Practicality and real-world impact
    - Code quality and documentation
    - Presentation/README clarity
    
    For ai_reasoning, provide a 2-3 sentence explanation of why you gave that score.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[{"url_context": {}}]  # Enables Gemini to visit the link
        )
    )

    # Extract JSON from response (may be wrapped in markdown code blocks)
    response_text = response.text.strip()
    print(f"Raw response:\n{response_text}\n")  # Debug output
    
    # Remove markdown code blocks if present
    if "```json" in response_text:
        start = response_text.find("```json") + 7
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()
    elif "```" in response_text:
        start = response_text.find("```") + 3
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()
    
    data = json.loads(response_text)

    # 2. Insert into your SQL table
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    print(f"Adding hack: {data['name']} with status: {status}")
    print(f"AI Score: {data['ai_score']}/10 - {data['ai_reasoning']}")
    c.execute('''
        INSERT INTO hacks (name, framework, githubLink, place, topic, descriptions, ai_score, ai_reasoning)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['name'], data['framework'], github_url, status, data['topic'], data['descriptions'], data['ai_score'], data['ai_reasoning']))
    
    conn.commit()
    conn.close()
    print(f"✅ Successfully added: {data['name']}")
    return True

def batch_insert_from_file(file_path, default_status=None):
    """
    Batch insert hackathon projects from a text file.
    
    File format options:
    1. URL, status (one per line): "https://github.com/user/repo, winner"
    2. URL only (uses default_status): "https://github.com/user/repo"
    
    Args:
        file_path: Path to the text file
        default_status: Default status if not specified per line (e.g., 'winner', 'participant')
    """
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    total = len([l for l in lines if l.strip()])
    success_count = 0
    failed = []
    
    print(f"\n📦 Starting batch insert of {total} projects...\n")
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):  # Skip empty lines and comments
            continue
        
        # Parse line - check if status is included
        if ',' in line:
            parts = line.split(',', 1)
            github_url = parts[0].strip()
            status = parts[1].strip()
        else:
            github_url = line
            status = default_status
        
        if not status:
            print(f"⚠️  Skipping {github_url} - no status provided")
            failed.append((github_url, "No status"))
            continue
        
        print(f"[{i}/{total}] Processing: {github_url}")
        
        try:
            auto_insert_hack(github_url, status)
            success_count += 1
        except Exception as e:
            print(f"❌ Failed: {e}")
            failed.append((github_url, str(e)))
    
    print(f"\n{'='*50}")
    print(f"✅ Batch insert complete: {success_count}/{total} successful")
    if failed:
        print(f"❌ Failed ({len(failed)}):")
        for url, error in failed:
            print(f"   - {url}: {error}")


def findTrendswithGemini(user_category, user_framework, user_description):
    """
    Analyze winning hackathon trends and provide advice based on user's project idea.
    
    Args:
        user_category: The category/topic of the user's project (e.g., AI, FinTech)
        user_framework: The framework/languages the user plans to use
        user_description: A description of the user's project idea
    """
    # Connect to database and fetch winning projects
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get the schema info
    schema = """
    TABLE: hacks
    COLUMNS:
        - id: INTEGER PRIMARY KEY AUTOINCREMENT
        - name: TEXT (Project Name)
        - framework: TEXT (Primary Framework/Languages used)
        - githubLink: TEXT (GitHub repository URL)
        - place: TEXT (Winner or Participant status)
        - topic: TEXT (Category like AI, FinTech, etc.)
        - descriptions: TEXT (Project summary)
        - tableNumber: INTEGER
        - ai_score: FLOAT (Winning potential rating 0.0-10.0)
        - ai_reasoning: TEXT (Explanation for the AI score)
    """
    
    # Fetch winners in the same category first (most relevant)
    c.execute("""
        SELECT name, framework, topic, descriptions, ai_score, ai_reasoning 
        FROM hacks 
        WHERE LOWER(place) LIKE '%winner%' AND LOWER(topic) LIKE ? 
        ORDER BY ai_score DESC 
        LIMIT 10
    """, (f'%{user_category.lower()}%',))
    category_winners = c.fetchall()
    
    # Fetch top winners from other categories for broader trends
    c.execute("""
        SELECT name, framework, topic, descriptions, ai_score, ai_reasoning 
        FROM hacks 
        WHERE LOWER(place) LIKE '%winner%' AND LOWER(topic) NOT LIKE ?
        ORDER BY ai_score DESC 
        LIMIT 10
    """, (f'%{user_category.lower()}%',))
    other_winners = c.fetchall()
    
    # Fetch some participants for comparison (lower scores)
    c.execute("""
        SELECT name, framework, topic, descriptions, ai_score, ai_reasoning 
        FROM hacks 
        WHERE LOWER(place) NOT LIKE '%winner%'
        ORDER BY ai_score DESC 
        LIMIT 5
    """)
    participants = c.fetchall()
    
    # Get aggregate stats
    c.execute("SELECT COUNT(*) FROM hacks WHERE LOWER(place) LIKE '%winner%'")
    total_winners = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM hacks")
    total_projects = c.fetchone()[0]
    
    c.execute("SELECT framework, COUNT(*) as cnt FROM hacks WHERE LOWER(place) LIKE '%winner%' GROUP BY framework ORDER BY cnt DESC LIMIT 5")
    top_frameworks = c.fetchall()
    
    c.execute("SELECT topic, COUNT(*) as cnt FROM hacks WHERE LOWER(place) LIKE '%winner%' GROUP BY topic ORDER BY cnt DESC LIMIT 5")
    top_categories = c.fetchall()
    
    c.execute("SELECT AVG(ai_score) FROM hacks WHERE LOWER(place) LIKE '%winner%'")
    avg_winner_score = c.fetchone()[0] or 0
    
    conn.close()
    
    # Format data as Markdown tables for better AI readability
    def format_projects_table(projects, title):
        if not projects:
            return f"### {title}\nNo projects found.\n"
        
        table = f"### {title}\n"
        table += "| Name | Framework | Category | Score | Description | Reasoning |\n"
        table += "|------|-----------|----------|-------|-------------|----------|\n"
        for name, framework, topic, desc, score, reasoning in projects:
            # Truncate long fields to keep table readable
            desc_short = (desc[:80] + "...") if desc and len(desc) > 80 else (desc or "N/A")
            reasoning_short = (reasoning[:60] + "...") if reasoning and len(reasoning) > 60 else (reasoning or "N/A")
            table += f"| {name} | {framework} | {topic} | {score}/10 | {desc_short} | {reasoning_short} |\n"
        return table + "\n"
    
    # Build structured data sections
    winners_in_category = format_projects_table(category_winners, f"Winners in '{user_category}' Category")
    winners_other = format_projects_table(other_winners, "Top Winners in Other Categories")
    participants_data = format_projects_table(participants, "Sample Participants (Non-Winners)")
    
    # Format aggregate stats as JSON-like structure
    stats_summary = f"""
### Database Statistics
- **Total Projects**: {total_projects}
- **Total Winners**: {total_winners}
- **Average Winner Score**: {avg_winner_score:.1f}/10

### Top Winning Frameworks
{chr(10).join([f"- {fw}: {cnt} wins" for fw, cnt in top_frameworks]) if top_frameworks else "No data yet"}

### Top Winning Categories
{chr(10).join([f"- {cat}: {cnt} wins" for cat, cnt in top_categories]) if top_categories else "No data yet"}
"""
    
    prompt = f"""
You are a hackathon strategy advisor. Analyze the following curated database of hackathon projects to identify winning trends and provide actionable advice.

## DATABASE SCHEMA
{schema}

## DATABASE STATISTICS & TRENDS
{stats_summary}

## RELEVANT DATA (Prioritized for your analysis)

{winners_in_category}
{winners_other}
{participants_data}

## USER'S PROJECT IDEA
- **Category/Topic**: {user_category}
- **Framework/Technologies**: {user_framework}
- **Project Description**: {user_description}

---

Please provide a focused analysis:

1. **Winning Trends Analysis**: What patterns do you see among winning projects? (common frameworks, popular categories, what differentiates winners from participants)

2. **Category-Specific Insights**: Based on winners in '{user_category}', what makes projects stand out in this space?

3. **Framework Recommendation**: Is '{user_framework}' commonly used by winners? Based on the top frameworks data, should they consider alternatives?

4. **Comparison to Winners**: How does the user's project idea compare to the winners shown? What are the gaps?

5. **Actionable Recommendations**: 3-5 specific, concrete suggestions to improve their chances of winning.

6. **Pitch Tips**: Based on how winning projects are described, how should they present their idea?

Be specific and reference actual projects from the data when giving advice.
"""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

if __name__ == "__main__":
    print("Starting insert and correlation process...")
    print("Options:")
    print("  1 - Insert a single hackathon project")
    print("  2 - Find trends with Gemini")
    print("  3 - Batch insert from file")
    print("  4 - Exit")
    choice = input("Enter your choice: ")
    if choice == '1':
        github_url = input("Enter the GitHub URL of the project: ")
        status = input("Enter the status (e.g., winner, participant): ")
        auto_insert_hack(github_url, status)
    elif choice == '2':
        print("\n--- Hackathon Trend Analysis & Advice ---")
        user_category = input("Enter your project category (e.g., AI, FinTech, HealthTech): ")
        user_framework = input("Enter your framework/technologies (e.g., React, Python, TensorFlow): ")
        user_description = input("Describe your project idea: ")
        print("\nAnalyzing winning trends and generating advice...\n")
        trends = findTrendswithGemini(user_category, user_framework, user_description)
        print(f"Hackathon Strategy Advice:\n{trends}")
    elif choice == '3':
        print("\n--- Batch Insert from File ---")
        print("File format: One entry per line")
        print("  Option A: 'github_url, status' (e.g., https://github.com/user/repo, winner)")
        print("  Option B: 'github_url' only (you'll specify a default status)")
        file_path = input("Enter the path to your text file: ").strip().strip('"')
        default_status = input("Default status for entries without status (leave blank if all have status): ").strip()
        batch_insert_from_file(file_path, default_status if default_status else None)
    else:
        print("Exiting...")