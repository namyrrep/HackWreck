"""Configuration and shared constants for the HackWreck scraper."""
import os
from dotenv import load_dotenv
from google import genai

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Load environment variables from the project root
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

DB_PATH = os.path.join(SCRIPT_DIR, 'hackathons.db')

# Database Configuration
USE_SNOWFLAKE = os.getenv("USE_SNOWFLAKE", "false").lower() == "true"

# Snowflake Configuration (only used if USE_SNOWFLAKE=true)
SNOWFLAKE_CONFIG = {
    'user': os.getenv('SNOWFLAKE_USER'),
    'password': os.getenv('SNOWFLAKE_PASSWORD'),
    'account': os.getenv('SNOWFLAKE_ACCOUNT'),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
    'database': os.getenv('SNOWFLAKE_DATABASE', 'SNOWFLAKE_LEARNING_DB'),
    'schema': os.getenv('SNOWFLAKE_SCHEMA', 'PROJECTS')
}

# Google API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini client
client = genai.Client(api_key=GOOGLE_API_KEY)
