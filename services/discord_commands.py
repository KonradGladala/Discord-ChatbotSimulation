import asyncio
import yaml
from services.discord_bot import MyBot
import discord

BOTS_YAML = "data/bots.yaml"

# Configure intents
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True  # needed to read messages

# Load bots from YAML
with open(BOTS_YAML, "r") as yaml_file:
    data = yaml.safe_load(yaml_file)

bot_objects = [
    MyBot(bot_info["name"], bot_info["token_env"], intents)
    for bot_info in data["bots"]
]

async def main():
    # Start all bots concurrently
    await asyncio.gather(*(bot.start() for bot in bot_objects))

if __name__ == "__main__":
    asyncio.run(main())