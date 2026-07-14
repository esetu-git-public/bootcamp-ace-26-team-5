from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv("backend/.env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print("URL:", url)

try:
    client = create_client(url, key)
    result = client.table("users").select("*").limit(1).execute()
    print("SUCCESS")
    print(result.data)
except Exception as e:
    print("ERROR")
    print(type(e).__name__)
    print(e)