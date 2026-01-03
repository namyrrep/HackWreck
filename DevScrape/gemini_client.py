"""Gemini AI client for project analysis and trend detection."""
import json
import secrets
from google.genai import types

# Try to import caching - it may not be available in all versions
try:
    from google.genai import caching
    CACHING_AVAILABLE = True
except ImportError:
    CACHING_AVAILABLE = False
    print("Warning: Context caching not available in this version of google-genai")

from .config import client
from .db import (
    get_winners_by_framework, 
    get_winners_by_category,
    get_winners_excluding_category, 
    get_participants,
    get_top_winners,
    get_database_stats
)


def generate_wreck_me_pitch() -> str:
    """Generate a random, high-quality hackathon idea pitch (Markdown).

    Uses aggregate stats + top winners as inspiration, then asks Gemini to
    synthesize an original idea that borrows the *patterns* of winners.
    """

    stats = get_database_stats()
    top_winners = get_top_winners(limit=12)

    top_frameworks = [fw for fw, _cnt in (stats.get("top_frameworks") or [])]
    top_categories = [cat for cat, _cnt in (stats.get("top_categories") or [])]

    challenge_modifiers = [
        "No user accounts; demo works instantly",
        "Must work with unreliable network",
        "Privacy-first: do not store raw PII",
        "Offline-first mobile experience",
        "Requires a real-time component",
        "Uses a novel data source",
        "Includes an on-device / edge element",
        "Two-sided marketplace UX",
    ]

    chosen_frameworks = ", ".join(secrets.choice(top_frameworks) for _ in range(min(2, len(top_frameworks)))) if top_frameworks else "React + Python"
    chosen_category = secrets.choice(top_categories) if top_categories else "AI"
    chosen_modifier = secrets.choice(challenge_modifiers)

    winners_bullets = ""
    for row in top_winners:
        row = list(row) if row is not None else []
        name = row[0] if len(row) > 0 else "N/A"
        framework = row[1] if len(row) > 1 else "N/A"
        topic = row[2] if len(row) > 2 else "N/A"
        desc = row[3] if len(row) > 3 else ""
        score = row[4] if len(row) > 4 else "?"
        winners_bullets += f"- **{name}** ({topic}) — {framework} — {score}/10 — {desc}\n"

    prompt = f"""
You are an elite hackathon pitch writer and product strategist.

Your job: generate ONE fresh hackathon project idea that is a *10/10 pitch*.

Constraints:
- The idea must be ORIGINAL (do not copy any project below).
- It should *combine the best parts* of winning patterns: clear user story, strong demo, unique differentiator, tight scope.
- Make it a GOOD CHALLENGE: ambitious but shippable in 24-48 hours.
- Output MUST be beautifully formatted Markdown.

Inspiration (top winners from our database):
{winners_bullets}

Use these as your default direction:
- Target category: **{chosen_category}**
- Suggested stack: **{chosen_frameworks}**
- Challenge modifier: **{chosen_modifier}**

Return EXACTLY this structure (Markdown only):

# Wreck Me

## Project Name

## One-line Hook

## The Problem (pain + stakes)

## The Solution (what the demo shows)

## Why This Wins (judge-facing)
- 5 bullets max

## Secret Sauce (the differentiator)

## Tech Stack
- bullets

## Demo Script (90 seconds)
1. ...

## MVP Checklist (ship in 6 hours)
- bullets

## Stretch Goals (if time)
- bullets

## Scoring Map
- **Impact**: ...
- **Technical difficulty**: ...
- **Design / UX**: ...
- **Novelty**: ...

Keep it sharp, vivid, and practical. No fluff.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text


def parse_json_response(response_text):
    """
    Parse JSON from Gemini response, handling markdown code blocks.
    
    Args:
        response_text: Raw response text from Gemini
        
    Returns:
        dict: Parsed JSON data
    """
    response_text = response_text.strip()
    
    # Remove markdown code blocks if present
    if "```json" in response_text:
        start = response_text.find("```json") + 7
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()
    elif "```" in response_text:
        start = response_text.find("```") + 3
        end = response_text.find("```", start)
        response_text = response_text[start:end].strip()
    
    return json.loads(response_text)


def analyze_github_project(github_url, status):
    """
    Analyze a GitHub repository and extract project information.
    
    Args:
        github_url: GitHub repository URL
        status: Winner or participant status
        
    Returns:
        dict: Extracted project data including name, framework, topic, etc.
    """
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

    print(f"Raw response:\n{response.text}\n")  # Debug output
    return parse_json_response(response.text)


def analyze_project_for_hackathon(github_url, hackathon_name, hackathon_theme=""):
    """
    Analyze an existing GitHub project and provide suggestions for a specific hackathon
    based on previous winning projects in the database.
    
    Args:
        github_url: The GitHub URL of the user's current project
        hackathon_name: Name of the hackathon they're planning to enter
        hackathon_theme: Optional theme/track of the hackathon
        
    Returns:
        dict: Contains project analysis, suggestions, and related winners
    """
    # First, analyze the user's GitHub project
    project_analysis_prompt = f"""
    Analyze this GitHub repository: {github_url}
    
    Focus on the ACTUAL CODE and project structure. Analyze:
    - The README, code files, and project architecture
    - Technical implementation quality
    - Feature completeness for a hackathon demo
    - Code organization and documentation
    
    DO NOT mention GitHub stars, forks, or community engagement - this is a hackathon project.
    
    Extract and return ONLY a JSON object:
    {{
        "name": "Project Name",
        "framework": "Primary Framework/Languages used",
        "topic": "Category (AI, FinTech, HealthTech, etc.)",
        "description": "2-3 sentence summary of what it does",
        "strengths": ["code-based strength 1", "code-based strength 2", "code-based strength 3"],
        "weaknesses": ["code-based weakness 1", "code-based weakness 2", "code-based weakness 3"],
        "current_score": 0.0
    }}
    
    For strengths/weaknesses, focus on:
    - Code quality and architecture
    - Feature implementation
    - Demo-readiness
    - Technical innovation
    - Documentation quality
    
    Rate current_score from 0.0 to 10.0 based on hackathon-readiness.
    """
    
    project_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=project_analysis_prompt,
        config=types.GenerateContentConfig(
            tools=[{"url_context": {}}]
        )
    )
    
    project_data = parse_json_response(project_response.text)
    
    # Get the user's project framework and topic for matching
    user_framework = project_data.get('framework', '').lower()
    user_topic = project_data.get('topic', '').lower()
    
    # Fetch relevant winners from database
    framework_winners = get_winners_by_framework(user_framework, limit=5)
    topic_winners = get_winners_by_category(user_topic, limit=5)
    
    # Combine and deduplicate related winners
    seen_names = set()
    related_winners = []
    for winner in framework_winners + topic_winners:
        if winner[0] not in seen_names:
            seen_names.add(winner[0])
            related_winners.append(winner)
    related_winners = related_winners[:6]  # Limit to 6
    
    # Get top winners overall and framework stats
    top_winners = get_top_winners(limit=5)
    stats = get_database_stats()
    top_frameworks = stats["top_frameworks"]
    
    # Format winner data
    def format_winners(winners):
        if not winners:
            return "No matching winners found."
        result = ""
        for name, framework, topic, desc, score, reasoning, github_link in winners:
            result += f"\n- **{name}** ({topic}) - Score: {score}/10\n  Framework: {framework}\n  {desc}\n"
        return result
    
    related_winners_text = format_winners(related_winners)
    top_winners_text = format_winners(top_winners)
    frameworks_text = "\n".join([f"- {fw}: {cnt} wins" for fw, cnt in top_frameworks]) if top_frameworks else "No data"
    
    # Cache expensive context for reuse (winning projects data)
    use_cache = None
    if CACHING_AVAILABLE:
        context_content = f"""## WINNING PROJECTS WITH SIMILAR FRAMEWORK OR CATEGORY
{related_winners_text}

## TOP WINNING PROJECTS OVERALL
{top_winners_text}

## MOST SUCCESSFUL FRAMEWORKS
{frameworks_text}"""
        
        try:
            cached_content = caching.CachedContent.create(
                model='gemini-2.5-flash',
                contents=[context_content],
                ttl="1800s"  # 30 minutes
            )
            use_cache = cached_content.name
        except Exception as e:
            print(f"Caching error: {e}")
            use_cache = None
    
    # Generate improvement suggestions
    suggestions_prompt = f"""
    You are a hackathon coach. A developer wants to enter their project into a hackathon and needs advice on how to improve it to maximize their chances of winning.

    ## HACKATHON DETAILS
    - **Hackathon Name**: {hackathon_name}
    - **Theme/Track**: {hackathon_theme if hackathon_theme else "General"}

    ## USER'S CURRENT PROJECT
    - **Name**: {project_data.get('name', 'Unknown')}
    - **Framework**: {project_data.get('framework', 'Unknown')}
    - **Category**: {project_data.get('topic', 'Unknown')}
    - **Description**: {project_data.get('description', 'No description')}
    - **Current Score**: {project_data.get('current_score', 'N/A')}/10
    - **Strengths**: {', '.join(project_data.get('strengths', []))}
    - **Weaknesses**: {', '.join(project_data.get('weaknesses', []))}

    ---

    Create a SLEEK, SCANNABLE improvement plan. Be EXTREMELY concise - no paragraphs, only bullet points.
    Search the web to find relevant tutorials, documentation, and resources.

    Format your response EXACTLY like this:

    ## STATUS: X/10 → Y/10
    *One sentence: biggest gap vs winners*

    ---

    ## PHASE 1: QUICK WINS (2-4h)
    
    **Task**: Brief 5-word description  
    → [Resource name](URL)
    
    **Task**: Brief 5-word description  
    → [Resource name](URL)
    
    **Task**: Brief 5-word description  
    → [Resource name](URL)

    ## PHASE 2: CORE IMPROVEMENTS (4-8h)
    
    **Task**: Brief 5-word description  
    → [Resource name](URL)
    
    **Task**: Brief 5-word description  
    → [Resource name](URL)

    ## PHASE 3: POLISH (2-4h)
    
    **Task**: Brief 5-word description  
    → [Resource name](URL)
    
    **Task**: Brief 5-word description  
    → [Resource name](URL)

    ---

    ## WINNER PATTERNS
    - Short insight 1
    - Short insight 2
    - Short insight 3

    ## YOUR PITCH
    *2 sentences max. Make it compelling.*

    ---

    CRITICAL: Keep tasks to 5-7 words max. Use real URLs. No fluff.
    """
    
    config_params = {
        "tools": [{"google_search": {}}]
    }
    if use_cache:
        config_params["cached_content"] = use_cache
    
    suggestions_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=suggestions_prompt,
        config=types.GenerateContentConfig(**config_params)
    )
    
    return {
        "project_analysis": project_data,
        "suggestions": suggestions_response.text,
        "related_winners": [{"name": w[0], "framework": w[1], "topic": w[2], "score": w[4], "githubLink": w[6] if len(w) > 6 else None} for w in related_winners],
        "hackathon_name": hackathon_name,
        "hackathon_theme": hackathon_theme
    }


def find_trends_with_gemini(user_category, user_framework, user_description):
    """
    Analyze winning hackathon trends and provide advice based on user's project idea.
    
    Args:
        user_category: The category/topic of the user's project
        user_framework: The framework/languages the user plans to use
        user_description: A description of the user's project idea
        
    Returns:
        str: Formatted trend analysis and advice
    """
    # Fetch winners in the same category first (most relevant)
    category_winners = get_winners_by_category(user_category, limit=10)
    
    # Fetch top winners from other categories for broader trends
    other_winners = get_winners_excluding_category(user_category, limit=10)
    
    # Fetch some participants for comparison
    participants = get_participants(limit=5)
    
    # Get aggregate stats
    stats = get_database_stats()
    
    # Format data as Markdown tables
    def format_projects_table(projects, title):
        if not projects:
            return f"### {title}\nNo projects found.\n"
        
        table = f"### {title}\n"
        table += "| Name | Framework | Category | Score | Description | Reasoning |\n"
        table += "|------|-----------|----------|-------|-------------|----------|\n"
        for row in projects:
            # Different DB backends / queries may include extra columns (e.g., githubLink).
            # Be tolerant and only use the first 6 fields we need.
            row = list(row) if row is not None else []
            name = row[0] if len(row) > 0 else "N/A"
            framework = row[1] if len(row) > 1 else "N/A"
            topic = row[2] if len(row) > 2 else "N/A"
            desc = row[3] if len(row) > 3 else None
            score = row[4] if len(row) > 4 else None
            reasoning = row[5] if len(row) > 5 else None
            # Truncate long fields
            desc_short = (desc[:80] + "...") if desc and len(desc) > 80 else (desc or "N/A")
            reasoning_short = (reasoning[:60] + "...") if reasoning and len(reasoning) > 60 else (reasoning or "N/A")
            table += f"| {name} | {framework} | {topic} | {score}/10 | {desc_short} | {reasoning_short} |\n"
        return table + "\n"
    
    # Build structured data sections
    winners_in_category = format_projects_table(category_winners, f"Winners in '{user_category}' Category")
    winners_other = format_projects_table(other_winners, "Top Winners in Other Categories")
    participants_data = format_projects_table(participants, "Sample Participants (Non-Winners)")
    
    # Format aggregate stats
    stats_summary = f"""
### Database Statistics
- **Total Projects**: {stats['total_projects']}
- **Total Winners**: {stats['total_winners']}
- **Average Winner Score**: {stats['avg_winner_score']:.1f}/10

### Top Winning Frameworks
{chr(10).join([f"- {fw}: {cnt} wins" for fw, cnt in stats['top_frameworks']]) if stats['top_frameworks'] else "No data yet"}

### Top Winning Categories
{chr(10).join([f"- {cat}: {cnt} wins" for cat, cnt in stats['top_categories']]) if stats['top_categories'] else "No data yet"}
"""
    use_cache = None
    if CACHING_AVAILABLE:
        context_content = f"""{stats_summary}

{winners_in_category}

{winners_other}

{participants_data}"""
        
        try:
            cached_content = caching.CachedContent.create(
                model='gemini-2.5-flash',
                contents=[context_content],
                ttl="1800s"  # 30 minutes
            )
            use_cache = cached_content.name
        except Exception as e:
            print(f"Caching error: {e}")
            use_cache = None
    
    prompt = f"""
You are a tough but constructive hackathon mentor. Analyze the database and provide a professional, critical analysis.

## DATABASE CONTEXT
{stats_summary}

{winners_in_category}

{winners_other}

{participants_data}

## USER'S PROJECT IDEA
- **Category**: {user_category}
- **Tech Stack**: {user_framework}
- **The Pitch**: {user_description}

---

Format your response EXACTLY like this (use emojis and bullet points, NO TABLES):

# 🛠️ WRECK YOUR HACK

**Category:** {user_category}  
**Tech Stack:** {user_framework}  
**Your Pitch:** {user_description}

---

## 🔍 SIMILAR WINNING PROJECTS

List 3-5 winning projects from the database that are most relevant:

- **[Project Name]** (Score: X/10) — One sentence on what made it win
- **[Project Name]** (Score: X/10) — One sentence on what made it win
- **[Project Name]** (Score: X/10) — One sentence on what made it win

---

## 🏆 WHAT WINNERS DO

Short, actionable patterns from the database:

- **Solve a specific problem** → "[Project Name] did X" — Do this: [actionable advice]
- **Use unique data/algorithms** → "[Project Name] used Y" — Do this: [actionable advice]
- **Clear MVP** → "[Project Name] focused on Z" — Do this: [actionable advice]
- **Justify their tech** → "[Project Name] chose X because..." — Do this: [actionable advice]
- **Demo impact** → "[Project Name] showed..." — Do this: [actionable advice]

---

## ⚠️ WHAT LOSERS DO

- **Vague Goals** — No clear metric for judges to evaluate. Fix: Define one measurable outcome.
- **Over-Ambition** — Half-finished features hurt you. Fix: Cut scope to one polished feature.
- **No "Why"** — "It's fast" isn't enough. Fix: Explain why {user_framework} is essential for this problem.
- **Generic Solution** — Nothing unique. Fix: Find your differentiator from the winners above.
- **Poor Demo** — Backend-heavy with no visual. Fix: Build a simple UI that shows value in 30 seconds.

---

## ⚖️ YOUR VERDICT

**Score: X/10**

### ✅ Strengths
- [Strength 1 with specific context]
- [Strength 2 with specific context]

### ❌ Gaps (The "Wrecking" Part)
- **[Gap 1]** — How to fix it in one sentence
- **[Gap 2]** — How to fix it in one sentence
- **[Gap 3]** — How to fix it in one sentence

---

## 🚀 TOP 3 ACTIONS (Do This Today)

1. **[Action]** — One specific, actionable sentence
2. **[Action]** — One specific, actionable sentence
3. **[Action]** — One specific, actionable sentence

---

## 🎙️ YOUR WINNING PITCH

> "[One compelling sentence that incorporates your tech stack and unique value]"

---

**CRITICAL INSTRUCTIONS:**
- Reference SPECIFIC project names from the database — use their actual names
- Keep every bullet to 1-2 sentences max
- Be brutally honest about gaps - this is the "wrecking" part
- Every action must be specific and doable, not generic advice
- NO TABLES — use bullet points only
"""
    
    config_params = {}
    if use_cache:
        config_params["cached_content"] = use_cache
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(**config_params) if config_params else None
    )
    return response.text
