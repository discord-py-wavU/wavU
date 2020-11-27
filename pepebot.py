import os

import discord
from discord.ext import commands

import config

client = commands.Bot(command_prefix=config.prefix)


@client.event
async def on_ready():
    await client.change_presence(status=config.status, activity=discord.Game(config.game))


@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')


@client.command()
async def reload(ctx, extension):
    try:
        client.unload_extension(f'cogs.{extension}')
    except discord.ext.commands.errors.ExtensionNotLoaded:
        print('Extension already unloaded')
    finally:
        client.load_extension(f'cogs.{extension}')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(config.token)
