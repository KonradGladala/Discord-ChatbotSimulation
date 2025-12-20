import logging
import discord
import random
from typing import List, Dict

import os
import logging
import discord

import os
import logging
import discord

async def get_last_messages(bot: discord.Client, channel_id: int = None, limit: int = 10) -> str:
    # Use env fallback if channel_id not provided
    if channel_id is None:
        try:
            channel_id = int(os.getenv("MAIN_CHANNEL_STANDARD", ""))
        except ValueError:
            logging.error("Invalid or missing MAIN_CHANNEL_STANDARD env variable")
            return ""

    # Fetch the channel
    try:
        channel = await bot.fetch_channel(channel_id)
    except discord.NotFound:
        logging.warning(f"Channel {channel_id} not found")
        return ""
    except discord.Forbidden:
        logging.warning(f"Missing permissions for channel {channel_id}")
        return ""

    # Fetch messages and format them
    messages = [
        f"{msg.author.display_name}: {msg.content}"
        async for msg in channel.history(limit=limit, oldest_first=False)
    ]
    messages.reverse()  # chronological order

    history_text = "\n".join(messages)
    logging.info(f"Fetched last {limit} messages from channel {channel_id}:\n{history_text}")
    return history_text




async def send_message_to_main_channels(bot: discord.Client, bot_name: str, message: str, guilds: List[Dict]):
    """
    Sends a message to the main_channel_id of every guild.
    `guilds` is a list of dicts with keys 'guild_id', 'main_channel_id', 'all_channel_ids'.
    """
    logging.info(f"{bot_name}: sending message to all main channels...")
    for guild in guilds:
        main_channel_id = guild["main_channel_id"]
        try:
            channel = await bot.fetch_channel(main_channel_id)
            await channel.send(message)
            logging.info(f"{bot_name}: message sent to {channel.name} ({channel.id})")
        except discord.NotFound:
            logging.warning(f"{bot_name}: main channel {main_channel_id} not found")
        except discord.Forbidden:
            logging.warning(f"{bot_name}: missing permissions for main channel {main_channel_id}")
        except discord.HTTPException as e:
            logging.error(f"{bot_name}: failed to send message to main channel {main_channel_id}: {e}")


async def send_message_to_random_channels(bot: discord.Client, bot_name: str, message: str, guilds: List[Dict]):
    """
    Sends a message to a random channel from all_channel_ids for every guild.
    """
    logging.info(f"{bot_name}: sending message to a random channel per guild...")
    for guild in guilds:
        all_channels = guild.get("all_channel_ids", [])
        if not all_channels:
            logging.warning(f"{bot_name}: no channels found for guild {guild['guild_id']}")
            continue

        channel_id = random.choice(all_channels)
        try:
            channel = await bot.fetch_channel(channel_id)
            await channel.send(message)
            logging.info(f"{bot_name}: message sent to {channel.name} ({channel.id})")
        except discord.NotFound:
            logging.warning(f"{bot_name}: random channel {channel_id} not found")
        except discord.Forbidden:
            logging.warning(f"{bot_name}: missing permissions for random channel {channel_id}")
        except discord.HTTPException as e:
            logging.error(f"{bot_name}: failed to send message to random channel {channel_id}: {e}")
