import os
# pyrefly: ignore [missing-import]
from supabase import create_client, Client

if not os.getenv("DB_PROVIDER"):
    os.environ["DB_PROVIDER"] = "sqlite"

SUPABASE_URL = os.getenv("SUPABASE_URL")
# Use service key (Secret) by default for backend, fallback to anon (Publishable)
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

supabase = None

if os.getenv("DB_PROVIDER") == "supabase":
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("DB_PROVIDER is set to 'supabase' but SUPABASE_URL or SUPABASE_KEY/SUPABASE_ANON_KEY is missing in environment/env")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            print(f"Warning: Failed to initialize Supabase client: {e}")

