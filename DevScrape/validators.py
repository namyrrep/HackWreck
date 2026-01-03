"""URL validation utilities for GitHub repositories."""
import re
import requests


def validate_github_url(url):
    """
    Validate GitHub URL format and check if repository exists.
    
    Args:
        url: GitHub repository URL to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    # Check URL format
    pattern = r'^https?://(?:www\.)?github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9._-]+?)(?:\.git)?/?$'
    match = re.match(pattern, url)
    
    if not match:
        return False, "Invalid GitHub URL format. Expected: https://github.com/username/repo"
    
    username, repo = match.groups()
    
    # Remove .git suffix if present
    repo = repo.rstrip('.git')
    
    # Check if repository exists
    api_url = f"https://api.github.com/repos/{username}/{repo}"
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 404:
            return False, f"Repository not found: {username}/{repo} (404)"
        elif response.status_code == 403:
            # Rate limited or private repo - allow it through
            print(f"Warning: Could not verify {username}/{repo} (rate limited or private)")
            return True, None
        elif response.status_code != 200:
            return False, f"Could not verify repository (HTTP {response.status_code})"
        
        # Check if it's actually a repo (not a user profile, etc.)
        data = response.json()
        if not data.get('name'):
            return False, "URL does not point to a valid repository"
            
        return True, None
    except requests.exceptions.RequestException as e:
        return False, f"Network error checking repository: {str(e)}"
