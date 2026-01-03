"""Gemini AI client for project analysis and trend detection."""
import json
from google.genai import types
from .config import client
from .database import (
    get_winners_by_framework, 
    get_winners_by_category,
    get_winners_excluding_category, 
    get_participants,
    get_top_winners,
    get_database_stats
)


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
    
    Extract and return ONLY a JSON object:
    {{
        "name": "Project Name",
        "framework": "Primary Framework/Languages used",
        "topic": "Category (AI, FinTech, HealthTech, etc.)",
        "description": "2-3 sentence summary of what it does",
        "strengths": ["strength1", "strength2", "strength3"],
        "weaknesses": ["weakness1", "weakness2", "weakness3"],
        "current_score": 0.0
    }}
    
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
    related_winners = related_winners[:8]  # Limit to 8
    
    # Get top winners overall and framework stats
    top_winners = get_top_winners(limit=5)
    stats = get_database_stats()
    top_frameworks = stats["top_frameworks"]
    
    # Format winner data
    def format_winners(winners):
        if not winners:
            return "No matching winners found."
        result = ""
        for name, framework, topic, desc, score, reasoning in winners:
            result += f"\n- **{name}** ({topic}) - Score: {score}/10\n  Framework: {framework}\n  {desc}\n"
        return result
    
    related_winners_text = format_winners(related_winners)
    top_winners_text = format_winners(top_winners)
    frameworks_text = "\n".join([f"- {fw}: {cnt} wins" for fw, cnt in top_frameworks]) if top_frameworks else "No data"
    
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

    ## WINNING PROJECTS WITH SIMILAR FRAMEWORK OR CATEGORY
    {related_winners_text}

    ## TOP WINNING PROJECTS OVERALL
    {top_winners_text}

    ## MOST SUCCESSFUL FRAMEWORKS
    {frameworks_text}

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
    
    suggestions_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=suggestions_prompt,
        config=types.GenerateContentConfig(
            tools=[{"google_search": {}}]  # Enable web search for resources
        )
    )
    
    return {
        "project_analysis": project_data,
        "suggestions": suggestions_response.text,
        "related_winners": [{"name": w[0], "framework": w[1], "topic": w[2], "score": w[4]} for w in related_winners],
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
        for name, framework, topic, desc, score, reasoning in projects:
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
    
    prompt = f"""
You are a hackathon judge. Analyze the database and give DIRECT, CONCISE answers.

## DATABASE STATS
{stats_summary}

## WINNERS IN '{user_category}' CATEGORY
{winners_in_category}

## OTHER TOP WINNERS
{winners_other}

## NON-WINNERS (FOR COMPARISON)
{participants_data}

## USER'S IDEA
- Category: {user_category}
- Framework: {user_framework}
- Description: {user_description}

---

Format your response EXACTLY like this:

## WHAT WINNERS DO

| Pattern | Example from Data |
|---------|------------------|
| Pattern 1 | "Project X did this..." |
| Pattern 2 | "Project Y shows..." |
| Pattern 3 | ... |
| Pattern 4 | ... |
| Pattern 5 | ... |

## WHAT LOSERS DO

| Mistake | Why It Fails |
|---------|-------------|
| Mistake 1 | Brief reason |
| Mistake 2 | Brief reason |
| Mistake 3 | Brief reason |

## YOUR IDEA: VERDICT

**Score: X/10**

### Strengths (What Sets You Apart)
- Strength 1
- Strength 2

### Gaps (What's Missing vs Winners)
- Gap 1 - How to fix
- Gap 2 - How to fix

## TOP 3 ACTIONS

1. **Action 1**: One sentence max
2. **Action 2**: One sentence max
3. **Action 3**: One sentence max

## YOUR WINNING PITCH
> Write a 2-sentence pitch they should use based on winner patterns.

Be brutally honest. Reference specific projects from the data. No fluff.
"""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text
