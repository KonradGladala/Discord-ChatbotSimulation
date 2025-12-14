from supabase import acreate_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


class BaseRepository:
    """Base repository that automatically initializes the Supabase client."""

    def __init__(self):
        self.client = None

    async def init_client(self):
        """Initialize the Supabase client if not already done."""
        if self.client is None:
            self.client = await acreate_client(SUPABASE_URL, SUPABASE_KEY)
        return self.client

    @classmethod
    async def create(cls):
        """Async factory: returns a repository instance with client ready."""
        self = cls()
        await self.init_client()
        return self