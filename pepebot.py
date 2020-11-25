import discord
from discord.utils import get
from discord.ext import commands
from config import token
import os

client = commands.Bot(command_prefix='=')

#events

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game('AAAAAAAAAA'))

@client.event
async def on_message(message):
    if message.content == 'eh vo':
        await message.author.send('que te pasa gil?')
    await client.process_commands(message)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


client.run(token)

