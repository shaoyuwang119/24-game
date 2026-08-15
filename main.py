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
@app_commands.describe(rounds="Number of rounds the game should go for.")
async def game(ia: discord.Interaction, rounds: int):
    await ia.response.send_message("Starting a 5-round 24-game...")
    session = GameSession(rounds, ia.channel, bot, ds, TIMEOUT)  # type: ignore
    await start_round(session)


bot.run(TOKEN)
