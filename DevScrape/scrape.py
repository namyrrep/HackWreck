import sqlite3
import json
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)

def auto_insert_hack(github_url, status):
    # 1. Ask Gemini to analyze the GitHub link
    prompt = f"""
    Analyze this GitHub repository: {github_url}. 
    The project was a '{status}' in a hackathon.
    Extract the following information and return it ONLY as a JSON object:
    {{
        "name": "Project Name",
        "framework": "Primary Framework/Languages",
        "topic": "Category like AI, FinTech, etc.",
        "descriptions": "A 2-sentence summary of what it does"
    }}
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
    conn = sqlite3.connect('hackathons.db')
    c = conn.cursor()
    print(f"Adding hack: {data['name']} with status: {status}")
    c.execute('''
        INSERT INTO hacks (name, framework, githubLink, place, topic, descriptions)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['name'], data['framework'], github_url, status, data['topic'], data['descriptions']))
    
    conn.commit()
    conn.close()
    print(f"✅ Successfully added: {data['name']}")

if __name__ == "__main__":
    print("Starting auto-insert process...")
    print("Type 'stop' at any prompt to exit.\n")
    
    while True:
        status = input("Status (win/lose): ").strip().lower()
        if status == "stop":
            break
        
        github_url = input("GitHub URL: ").strip()
        if github_url == "stop":
            break
        
        auto_insert_hack(github_url, status)
        print()  # Empty line for readability
    
    print("Process completed.")