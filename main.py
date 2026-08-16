import os
from typing import Any
import discord
import asyncio
import random
import re
import ast
import datetime
from discord import app_commands
from discord.ext import commands
from simpleeval import SimpleEval
from dotenv import load_dotenv
from datasets import load_dataset
from keep_alive import keep_alive

from gameObjects import *

ds = load_dataset("nlile/24-game", split="train")

load_dotenv()
TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

TIMEOUT = 40


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


@bot.tree.command(name="game", description="Starts a game of 24-Game.")
@app_commands.describe(rounds="Number of rounds the game should go for (default 5).")
@app_commands.describe(timer="Number of seconds to answer each round (default 30).")
async def game(ia: discord.Interaction, rounds: int = 5, timer: int = 30):

    if rounds > 30:
        await ia.response.send_message("Maximum allowed rounds is 30.", ephemeral=True)
        return

    if timer > 180:
        await ia.response.send_message("Maximum timer is 120 seconds!", ephemeral=True)
        return

    await ia.response.send_message(
        f"Starting a {rounds}-round 24-game, timer {timer} secs... "
    )
    await asyncio.sleep(3)
    session = GameSession(rounds, ia.channel, bot, ds, timer)  # type: ignore
    await start_round(session)


keep_alive()
bot.run(TOKEN)
