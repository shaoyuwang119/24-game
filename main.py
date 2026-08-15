import discord as dc
import os
from dotenv import load_dotenv

load_dotenv()

intents = dc.Intents.default()
intents.message_content = True
client = dc.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.content == '!ping':
        await message.channel.send('Pong!')

client.run(os.getenv('DISCORD_TOKEN'))