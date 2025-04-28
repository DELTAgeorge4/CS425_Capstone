import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
VT_API_KEY    = os.getenv("VT_API_KEY")
JWT_SECRET    = os.getenv("JWT_SECRET")
