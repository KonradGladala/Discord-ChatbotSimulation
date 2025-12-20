import asyncio
import yaml
import sys
import discord
from services.discord_bot import MyBot
from dotenv import load_dotenv
from services.path_helper import get_file

load_dotenv()

if len(sys.argv) < 2:
    print("Usage: python run_single_bot.py <BOT_TOKEN_ENV>")
    sys.exit(1)

token_env = sys.argv[1]

# Load intents
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

# Load bot info from YAML
BOTS_YAML = get_file("data", "bots.yaml")
with open(BOTS_YAML) as f:
    data = yaml.safe_load(f)

bot_info = next((b for b in data["bots"] if b["data"]["token_env"] == token_env), None)
if not bot_info:
    print(f"No bot info found for {token_env}")
    sys.exit(1)

# Run bot
bot = MyBot(name=bot_info["name"], token_env=token_env, prompts=bot_info["data"]["prompts"], intents=intents)

async def main():
    # Start bot and keep it running indefinitely
    async with bot:
        await bot.cleanup_deleted_guilds()
        await asyncio.Event().wait()  # keep running

asyncio.run(main())
