from supabase import acreate_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async def init_supabase(): 
    return await acreate_client(SUPABASE_URL, SUPABASE_KEY)

async def close_supabase(supabase_client):
        await supabase_client.close()

