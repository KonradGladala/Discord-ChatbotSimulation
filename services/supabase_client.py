from supabase import acreate_client
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()  # load .env automatically

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create a global async client properly
supabase_client = asyncio.run(acreate_client(SUPABASE_URL, SUPABASE_KEY))