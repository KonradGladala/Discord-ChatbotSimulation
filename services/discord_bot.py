import os
import logging
import asyncio
import discord
from discord.ext import commands
from repositories.discord_bot_repository import DiscordBotRepository
from cogs.setup import SetupCog
import ast

logging.basicConfig(level=logging.INFO)

class MyBot:
    DEFAULT_INTENTS = discord.Intents.default()
    DEFAULT_INTENTS.guilds = True
    DEFAULT_INTENTS.messages = True
    DEFAULT_INTENTS.message_content = True

    def __init__(self, name: str, token_env: str, prompts: dict[str, str], intents=None):
        self.name = name
        self.token = os.getenv(token_env)
        self.intents = intents or self.DEFAULT_INTENTS

        self.basePrompt = os.getenv(prompts["BASE_PROMPT"])
        self.rarePrompt = os.getenv(prompts["RARE_PROMPT"])

        self.bot = commands.Bot(command_prefix="!", intents=self.intents)
        self.bot.setup_hook = self._setup_hook
        self.bot.event(self.on_ready)

        self.guild_channels = []
        self._connect_task = None

    async def _setup_hook(self):
        await self.bot.add_cog(SetupCog(self.bot, self.name))
        await self.bot.tree.sync()
        logging.info(f"{self.name}: commands synced")

    async def on_ready(self):
        logging.info(f"{self.name}: ready as {self.bot.user}")

    async def cleanup_deleted_guilds(self):
        repo = await DiscordBotRepository().create()
        for guild in self.guild_channels:
            try:
                await self.bot.fetch_channel(guild["main_channel_id"])
            except (discord.NotFound, discord.Forbidden):
                logging.info(f"{self.name}: removing unavailable guild {guild['guild_id']}")
                await repo.delete_guild(self.name, guild["guild_id"])

    async def __aenter__(self):
        logging.info(f"{self.name}: connecting bot...")
        try:
            await self.bot.login(self.token)
            self._connect_task = asyncio.create_task(self.bot.connect())
            await self.bot.wait_until_ready()
        except Exception as e:
            logging.exception(f"{self.name}: failed to connect: {e}")
            raise

        # Fetch and parse guild channels
        repo = await DiscordBotRepository().create()
        guild_data = await repo.get_guild_channels(self.name)

        self.guild_channels = []
        for guild in guild_data:
            main_id = int(guild["main_channel_id"])
            all_ids_raw = guild.get("all_channel_ids", [])
            all_ids = (
                [int(i) for i in ast.literal_eval(all_ids_raw)]
                if isinstance(all_ids_raw, str)
                else [int(i) for i in all_ids_raw]
            )
            self.guild_channels.append({
                "guild_id": guild["guild_id"],
                "main_channel_id": main_id,
                "all_channel_ids": all_ids
            })

        logging.info(f"{self.name}: __aenter__ completed, bot task running.")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._connect_task:
            await self.bot.close()
            await self._connect_task
        logging.info(f"{self.name}: disconnected cleanly")
