# HackWreck

A hackathon project analyzer that uses AI to identify winning trends and provide strategic advice for future hackathon participants.

> **Submission for the Hacks for Hackers hackathon**

## Features

-  **Auto-analyze GitHub repos** - Gemini extracts project details, frameworks, and categories
-  **AI Scoring** - Each project gets a "winning potential" score (0-10) with reasoning
-  **Trend Analysis** - Find patterns among winning projects
-  **Strategic Advice** - Get personalized recommendations based on your project idea
-  **Batch Import** - Bulk insert projects from a text file

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/HackWreck.git
cd HackWreck
```

### 2. Install dependencies
```bash
pip install google-genai python-dotenv
```

### 3. Set up environment variables
Create a `.env` file in the `DevScrape/` folder:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

> Get your API key from [Google AI Studio](https://aistudio.google.com/apikey)

### 4. Initialize the database
```bash
cd DevScrape
python devWeb.py
```

## Usage

Run the main script:
```bash
python scrape.py
```

### Options:
1. **Insert a single project** - Analyze a GitHub repo and add to database
2. **Find trends with Gemini** - Get AI-powered advice for your hackathon idea
3. **Batch insert from file** - Import multiple projects from a text file
4. **Exit**

### Batch Import Format
Create a text file with one entry per line:
```
https://github.com/user/repo1, winner
https://github.com/user/repo2, participant
```

Or just URLs (specify default status when prompted):
```
https://github.com/user/repo1
https://github.com/user/repo2
```

## Project Structure

```
HackWreck/
├── README.md
├── DevScrape/
│   ├── scrape.py       # Main script with all functions
│   ├── devWeb.py       # Database initialization
│   ├── hackathons.db   # SQLite database (created on first run)
│   └── .env            # API keys (not committed)
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `google-genai` | Google Gemini AI API client |
| `python-dotenv` | Load environment variables from .env |
| `sqlite3` | Database (built into Python) |

## Database Schema

```sql
CREATE TABLE hacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    framework TEXT,
    githubLink TEXT,
    place TEXT,           -- 'Winner' or 'Participant'
    topic TEXT,           -- Category (AI, FinTech, etc.)
    descriptions TEXT,
    tableNumber INTEGER,
    ai_score FLOAT,       -- Winning potential (0.0-10.0)
    ai_reasoning TEXT     -- Explanation for the score
);
```

## License

MIT
