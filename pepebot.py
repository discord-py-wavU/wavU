import os
import discord
from cogs import db
from discord.ext import commands
import asyncio

import config

client = commands.Bot(command_prefix=config.prefix)


@client.event
async def on_ready():
    await client.change_presence(status=config.status, activity=discord.Game(config.game))
    await daily_task()


@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
                db.add_server(str(guild.name))
        break


@client.event
async def on_guild_remove(guild):
    db.server_delete(str(guild.name))


async def daily_task():
    servers = db.all_servers(False)
    guilds = client.guilds
    for guild in guilds:
        is_In = True
        repeated = 0
        for server in servers:
            if guild.name == server[1]:
                repeated += 1
                is_In = False
        if repeated == 2:
            db.server_delete(str(guild.name))
        if is_In:
            db.add_server(str(guild.name))

    await asyncio.sleep(24*60*60)
    await daily_task()


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(config.token)
