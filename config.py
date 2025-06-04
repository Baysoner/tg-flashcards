from dotenv import load_dotenv
import os

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

if not API_TOKEN:
    raise ValueError("No API_TOKEN found in .env file")
