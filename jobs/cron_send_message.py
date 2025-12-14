import os
import yaml
import asyncio
import random
import logging
import discord
from services.ai_service import AIMessageService
from services.discord_bot import MyBot
from repositories.discord_bot_repository import DiscordBotRepository
from services.path_helper import get_file
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOTS_YAML = get_file("data", "bots.yaml")

# Load bot config
with open(BOTS_YAML) as f:
    data = yaml.safe_load(f)

bots_list = data["bots"]

async def send_message(bot_info, message):
    intents = discord.Intents.default()
    intents.guilds = True
    intents.messages = True
    intents.message_content = True

    bot = MyBot(name=bot_info["name"], token_env=bot_info["token_env"], intents=intents)
    logging.info(f"{bot.name}: starting bot...")

    # Login and connect manually
    await bot.bot.login(bot.token)
    connect_task = asyncio.create_task(bot.bot.connect())

    # Wait until the bot is ready
    await bot.bot.wait_until_ready()

    # Your DB work
    repo = await DiscordBotRepository().create()
    guild_channels = await repo.get_guild_channels(bot.name)

    for gc in guild_channels:
        channel_id = gc["main_channel_id"]
        try:
            channel = await bot.bot.fetch_channel(channel_id)
            await channel.send(message)
            logging.info(f"{bot.name}: message sent to {channel.name} ({channel.id})")
        except discord.NotFound:
            logging.warning(f"{bot.name}: channel {channel_id} not found")
        except discord.Forbidden:
            logging.warning(f"{bot.name}: missing permissions for channel {channel_id}")
        except discord.HTTPException as e:
            logging.error(f"{bot.name}: failed to send message to channel {channel_id}: {e}")

    # Disconnect cleanly
    await bot.bot.close()
    await connect_task  # ensure connect task is awaited
    logging.info(f"{bot.name}: disconnected")

async def main():
    # Weighted random selection
    weights = [bot.get("weight", 1.0) for bot in bots_list]
    selected_bot = random.choices(bots_list, weights=weights, k=1)[0]

    logging.info(f"Selected bot: {selected_bot['name']} (weight={selected_bot.get('weight', 1.0)})")
    ai_service = AIMessageService()

    logging.info("Generating AI message...")
    ai_message = await ai_service.generate_message("Write 3 words only")
    logging.info("AI message generated.")
    
    await send_message(selected_bot, ai_message)

if __name__ == "__main__":
    asyncio.run(main())
