"""
HackWreck - Hackathon Project Scraper and Analyzer

Main entry point for the CLI interface. This module provides functions for:
- Inserting hackathon projects from GitHub URLs
- Batch inserting projects from files
- Analyzing projects for specific hackathons
- Finding trends based on winning projects
- Deleting projects by ID
"""
import os
from .validators import validate_github_url
from .database import check_duplicate_project, insert_project, delete_by_id
from .gemini_client import analyze_github_project, analyze_project_for_hackathon, find_trends_with_gemini
from .config import DB_PATH, GOOGLE_API_KEY, client



def auto_insert_hack(github_url, status):
    """
    Analyze a GitHub repository and insert it into the database.
    
    Args:
        github_url: GitHub repository URL
        status: Winner or participant status
        
    Returns:
        bool: True if successful, False if validation failed or duplicate
    """
    # Validate GitHub URL format and existence
    is_valid, error_msg = validate_github_url(github_url)
    if not is_valid:
        print(f"Validation failed: {error_msg}")
        return False
    
    # Check for duplicate link first
    exists, project_id, project_name = check_duplicate_project(github_url)
    if exists:
        print(f"Duplicate detected: '{project_name}' already exists with this GitHub link (ID: {project_id})")
        return False
    
    # Analyze the project using Gemini
    try:
        data = analyze_github_project(github_url, status)
    except Exception as e:
        print(f"Error analyzing project: {e}")
        return False
    
    # Insert into database
    print(f"Adding hack: {data['name']} with status: {status}")
    print(f"AI Score: {data['ai_score']}/10 - {data['ai_reasoning']}")
    
    success = insert_project(
        name=data['name'],
        framework=data['framework'],
        github_url=github_url,
        status=status,
        topic=data['topic'],
        descriptions=data['descriptions'],
        ai_score=data['ai_score'],
        ai_reasoning=data['ai_reasoning']
    )
    
    if success:
        print(f"Successfully added: {data['name']}")
    else:
        print(f"Failed to add project to database")
    
    return success


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
        print(f"File not found: {file_path}")
        return
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    total = len([l for l in lines if l.strip()])
    success_count = 0
    failed = []
    
    print(f"\nStarting batch insert of {total} projects...\n")
    
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
            print(f"Skipping {github_url} - no status provided")
            failed.append((github_url, "No status"))
            continue
        
        print(f"[{i}/{total}] Processing: {github_url}")
        
        try:
            if auto_insert_hack(github_url, status):
                success_count += 1
        except Exception as e:
            print(f"Failed: {e}")
            failed.append((github_url, str(e)))
    
    print(f"\n{'='*50}")
    print(f"Batch insert complete: {success_count}/{total} successful")
    if failed:
        print(f"Failed ({len(failed)}):")
        for url, error in failed:
            print(f"   - {url}: {error}")


def analyzeProjectForHackathon(github_url, hackathon_name, hackathon_theme=""):
    """
    Analyze an existing GitHub project and provide suggestions for a specific hackathon.
    
    Args:
        github_url: The GitHub URL of the user's current project
        hackathon_name: Name of the hackathon they're planning to enter
        hackathon_theme: Optional theme/track of the hackathon
        
    Returns:
        dict: Contains project analysis, suggestions, and related winners
    """
    return analyze_project_for_hackathon(github_url, hackathon_name, hackathon_theme)


def findTrendswithGemini(user_category, user_framework, user_description):
    """
    Analyze winning hackathon trends and provide advice based on user's project idea.
    
    Args:
        user_category: The category/topic of the user's project
        user_framework: The framework/languages the user plans to use
        user_description: A description of the user's project idea
        
    Returns:
        str: Formatted trend analysis and advice
    """
    return find_trends_with_gemini(user_category, user_framework, user_description)


if __name__ == "__main__":
    print("Starting insert and correlation process...")
    print("Options:")
    print("  1 - Insert a single hackathon project")
    print("  2 - Find trends with Gemini")
    print("  3 - Batch insert from file")
    print("  4 - Delete a project by ID")
    print("  5 - Exit")
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
        
    elif choice == '4':
        project_id = input("Enter the ID of the project to delete: ").strip()
        if project_id.isdigit():
            result = delete_by_id(int(project_id))
            print(result["message"])
        else:
            print("Invalid project ID. Please enter a numeric value.")
            
    elif choice == '5':
        print("Exiting...")
    else:
        print("Invalid choice. Exiting...")
