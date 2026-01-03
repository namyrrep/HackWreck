import sqlite3

def init_db():
    conn = sqlite3.connect('hackathons.db')
    c = conn.cursor()
    
    # Using an AUTOINCREMENT ID and default values
    c.execute('''
        CREATE TABLE IF NOT EXISTS hacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            framework TEXT,
            githubLink TEXT,
            place TEXT,         -- Store 'Winner' or 'Participant' (Loser)
            topic TEXT,         -- Gemini-generated Category
            descriptions TEXT,
            tableNumber INTEGER,
            ai_score FLOAT,     -- Gemini's rating of 'Winning Potential' (0.0-10.0)
            ai_reasoning TEXT   -- Gemini's explanation for the ai_score
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# How to add a hack
#name = "Sample Hackathon"
#framework = "Django"
#githubLink = "https://github.com/sample/sample-hackathon"
#place = "New York"
#topic = "Web Development"
#descriptions = "A sample hackathon for web development enthusiasts."
#tableNumber = 1
#Insert
#c.execute("INSERT INTO hacks (name, framework, githubLink, place, topic, descriptions, tableNumber) VALUES (?, ?, ?, ?, ?, ?, ?)", 
#          (name, framework, githubLink, place, topic, descriptions, tableNumber))
#important to save changes
#conn.commit()