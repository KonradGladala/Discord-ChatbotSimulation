import os
import logging
from discord.ext import commands
from cogs.setup import SetupCog

logging.basicConfig(level=logging.INFO)

class MyBot:
    def __init__(self, name, token_env, intents):
        self.name = name
        self.token = os.getenv(token_env)

        self.bot = commands.Bot(
            command_prefix="!",
            intents=intents
        )

        self.bot.setup_hook = self._setup_hook
        self.bot.event(self.on_ready)

    async def _setup_hook(self):
        await self.bot.add_cog(SetupCog(self.bot, self.name))

        # 🌍 global commands (multi-guild)
        await self.bot.tree.sync()

        logging.info(f"{self.name}: commands synced")

    async def on_ready(self):
        logging.info(f"{self.name}: ready as {self.bot.user}")

    async def start(self):
        await self.bot.start(self.token)