import asyncio
import yaml
from services.discord_bot import MyBot
from dotenv import load_dotenv
import discord

BOTS_YAML = "data/bots.yaml"
load_dotenv()

# Configure intents
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

# Load bots from YAML
with open(BOTS_YAML, "r") as yaml_file:
    data = yaml.safe_load(yaml_file)

bot_objects = [
    MyBot(
        name=bot_info["name"],
        token_env=bot_info["token_env"],
        intents=intents
    )
    for bot_info in data["bots"]
]

async def start_all_bots():
    tasks = []
    for bot in bot_objects:
        # Each bot runs in its own task
        tasks.append(asyncio.create_task(bot.start()))
    # Wait for all tasks to finish (they never will unless bots stop)
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(start_all_bots())
