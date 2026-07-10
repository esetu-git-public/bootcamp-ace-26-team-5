import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY is missing in .env")

# Strip '/rest/v1/' or '/rest/v1' from the URL if present
if SUPABASE_URL.endswith("/rest/v1/"):
    SUPABASE_URL = SUPABASE_URL[:-9]
elif SUPABASE_URL.endswith("/rest/v1"):
    SUPABASE_URL = SUPABASE_URL[:-8]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)