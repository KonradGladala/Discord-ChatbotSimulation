import logging
from discord.ext import commands
from discord import Interaction, app_commands
from repositories.discord_bot_repository import DiscordBotRepository

class SetupCog(commands.Cog):
    def __init__(self, bot, bot_name):
        self.bot = bot
        self.bot_name = bot_name

    @app_commands.command(
        name="setup",
        description="Configure this bot for this server"
    )
    async def setup(self, interaction: Interaction):
        logging.info(f"{self.bot_name}: /setup in guild {interaction.guild.id}")

        repo = await DiscordBotRepository().create()
        await repo.upsert(
            bot_name=self.bot_name,
            guild_id=interaction.guild.id,
            main_channel_id=interaction.channel.id,
            all_channel_ids=[c.id for c in interaction.guild.text_channels],
            irritation=0.0
        )

        await interaction.response.send_message(
            f"<@{self.bot.user.id}> configured for this server."
        )
