from discord.ext import commands
import os
import asyncio
import asyncpg

# Database config from environment
DB_URL = os.getenv("DATABASE_URL")  # Supabase/Postgres connection string

class MyBot:
    def __init__(self, name, token_env, intents):
        self.name = name
        self.token = os.getenv(token_env)
        self.bot = commands.Bot(command_prefix="/", intents=intents)
        self.bot.bot_name = name  # store bot name as an attribute
        self.add_commands()
        self.db_pool = None  # will be set in init_db()

    async def init_db(self):
        """Initialize the connection pool."""
        self.db_pool = await asyncpg.create_pool(dsn=DB_URL)

    def add_commands(self):
        @self.bot.command()
        async def setup(ctx):
            """Sets the main and all channels for the guild."""
            await self.update_channels(ctx.guild.id, ctx.channel.id, [c.id for c in ctx.guild.text_channels])
            await ctx.send(f"{self.name} is now successfully setup in this channel and will begin interacting.")

    async def update_channels(self, guild_id: int, main_channel_id: int, all_channel_ids: list):
        """Insert or update channels for a guild in the DB."""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO discord_bots (bot_name, guild_id, main_channel_id, all_channel_ids)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (bot_name, guild_id)
                DO UPDATE SET main_channel_id = EXCLUDED.main_channel_id,
                              all_channel_ids = EXCLUDED.all_channel_ids;
            """, self.name, str(guild_id), str(main_channel_id), str(all_channel_ids))  # store IDs as text

    async def get_channels(self, guild_id: int):
        """Retrieve main channel and all channels for a guild."""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT main_channel_id, all_channel_ids
                FROM discord_bots
                WHERE bot_name = $1 AND guild_id = $2;
            """, self.name, str(guild_id))

        if row:
            main_channel = int(row["main_channel_id"])
            all_channels = [int(cid) for cid in eval(row["all_channel_ids"])]
            return main_channel, all_channels
        return None, []

    async def start(self):
        """Start the bot after initializing DB connection."""
        if not self.db_pool:
            await self.init_db()
        await self.bot.start(self.token)