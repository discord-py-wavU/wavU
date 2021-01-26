import os

import discord
from discord.ext import commands

import config

client = commands.Bot(command_prefix=config.prefix)


@client.event
async def on_ready():
    await client.change_presence(status=config.status, activity=discord.Game(config.game))

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(config.token)
