from .base_repository import BaseRepository

class DiscordBotRepository(BaseRepository):
    """Repository for interacting with the discord_bots table."""

    async def get_guild_channels(self, bot_name: str):
        response = await self.client.table("discord_bots") \
            .select("guild_id,main_channel_id") \
            .eq("bot_name", bot_name) \
            .execute()
        return response.data or []

    async def upsert(self, bot_name: str, guild_id: int, main_channel_id: int, all_channel_ids: list):
        await self.client.table("discord_bots").upsert({
            "bot_name": bot_name,
            "guild_id": guild_id,
            "main_channel_id": main_channel_id,
            "all_channel_ids": all_channel_ids
        }).execute()