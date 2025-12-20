import os
import yaml
import asyncio
import random
import logging
from repositories.discord_bot_repository import DiscordBotRepository
from services.ai_service import AIMessageService
from services.discord_bot import MyBot
from services.discord_service import get_last_messages, send_message_to_main_channels
from services.path_helper import get_file
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOTS_YAML = get_file("data", "bots.yaml")

# Load bot config
with open(BOTS_YAML) as f:
    data = yaml.safe_load(f)

bots_list = data["bots"]

async def main():
    # Weighted random selection of bot
    weights = [bot.get("data", {}).get("weight", 1.0) for bot in bots_list]
    selected_bot = random.choices(bots_list, weights=weights, k=1)[0]
    logging.info(f"Selected bot: {selected_bot['name']} (weight={selected_bot['data'].get('weight', 1.0)})")

    repo = await DiscordBotRepository().create()
    ai_service = AIMessageService(repo)

    # Use the new MyBot context manager
    async with MyBot(selected_bot["name"], selected_bot["data"]["token_env"], selected_bot["data"]["prompts"]) as bot_conn:
        # Fetch last 5 messages for context
        conversation_context = await get_last_messages(bot_conn.bot, limit=8)

        # Generate AI message using conversation context
        logging.info("Generating AI message...")
        ai_message = await ai_service.generate_message(
            bot_conn,
            conversation_context=conversation_context
        )
        logging.info("AI message generated.")

        await send_message_to_main_channels(bot_conn.bot, bot_conn.name, ai_message, bot_conn.guild_channels)

if __name__ == "__main__":
    asyncio.run(main())
