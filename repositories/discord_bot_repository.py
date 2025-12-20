from .base_repository import BaseRepository

class DiscordBotRepository(BaseRepository):
    """Repository for interacting with the discord_bots table."""

    async def get_guild_channels(self, bot_name: str):
        response = await self.client.table("discord_bots") \
            .select("guild_id, main_channel_id, all_channel_ids") \
            .eq("bot_name", bot_name) \
            .execute()
        return response.data or []
    
    async def get_irritation(self, bot_name: str):
        response = await self.client.table("discord_bots") \
            .select("irritation") \
            .eq("bot_name", bot_name) \
            .execute()
        if response.data and len(response.data) > 0 and "irritation" in response.data[0]:
            return response.data[0]["irritation"]
        else: return 0.0

    async def upsert(self, bot_name: str, guild_id: int, main_channel_id: int | None = None,
    all_channel_ids: list | None = None, irritation: float | None = None):
        fields = {
        "bot_name": bot_name,
        "guild_id": guild_id,
        "main_channel_id": main_channel_id,
        "all_channel_ids": all_channel_ids,
        "irritation": irritation
        }

        # Keep only the keys with non-None values
        payload = {k: v for k, v in fields.items() if v is not None}

        if payload:  # only call upsert if there’s at least one field
            await self.client.table("discord_bots").upsert(payload).execute()

    async def update_irritation(self, bot_name: str, irritation: float):
        print(bot_name + " updating irritation to " + str(irritation))
        await self.client.table("discord_bots") \
            .update({"irritation": irritation}) \
            .eq("bot_name", bot_name) \
            .execute()

    async def delete_guild(self, bot_name: str, guild_id: int):
        await self.client.table("discord_bots") \
            .delete() \
            .eq("bot_name", bot_name) \
            .eq("guild_id", guild_id) \
            .execute()