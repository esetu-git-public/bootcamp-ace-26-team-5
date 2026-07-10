import os
# pyrefly: ignore [missing-import]
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
# Use service key (Secret) by default for backend, fallback to anon (Publishable)
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL or SUPABASE_KEY/SUPABASE_ANON_KEY is missing in environment/env")


# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
