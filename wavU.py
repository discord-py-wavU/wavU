import asyncio
import logging
import os

import discord
import discord.utils
from discord.ext import commands

import config
import content
from cogs import db

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=config.prefix, help_command=None, intents=intents)
logging.basicConfig(level=logging.INFO)


@client.event
async def on_ready():
    await client.change_presence(status=config.status, activity=discord.Game(config.game))
    logging.info("Bot is ready")
    await daily_task()


@client.command(aliases=['serv', 'ser'])
async def servers(ctx, arg=None):
    guilds = client.guilds

    if arg == "names":
        guilds = [guild.name for guild in guilds]
        await ctx.send(guilds)
    elif arg is None:
        await ctx.send("Amount of servers wavU is in: " + str(len(guilds)))
    else:
        await ctx.send("No valid argument")


@client.command(aliases=['Help'])
async def help(ctx):
    embed = discord.Embed(title=content.title, description=content.description, color=content.side_color)
    embed.set_thumbnail(url=content.img_link)
    embed.add_field(name=content.field_title_add, value=content.field_description_add, inline=False)
    embed.add_field(name=content.field_title_choose, value=content.field_description_choose, inline=False)
    embed.add_field(name=content.field_title_download, value=content.field_description_download, inline=False)
    embed.add_field(name=content.field_title_unzip, value=content.field_description_unzip, inline=False)
    embed.add_field(name=content.field_title_zip, value=content.field_description_zip, inline=False)
    embed.add_field(name=content.field_title_delete, value=content.field_description_delete, inline=False)
    embed.add_field(name=content.field_title_edit, value=content.field_description_edit, inline=False)
    embed.add_field(name=content.field_title_list, value=content.field_description_list, inline=False)
    embed.add_field(name=content.field_title_stop, value=content.field_description_stop, inline=False)
    embed.add_field(name=content.field_title_on, value=content.field_description_on, inline=False)
    embed.add_field(name=content.field_title_off, value=content.field_description_off, inline=False)
    embed.add_field(name=content.field_title_status, value=content.field_description_status, inline=False)
    embed.add_field(name=content.field_title_role, value=content.field_description_role, inline=False)
    embed.add_field(name=content.field_title_unrole, value=content.field_description_unrole, inline=False)
    embed.add_field(name=content.field_title_invite, value=content.field_description_invite, inline=False)
    embed.add_field(name=content.field_title_join, value=content.field_description_join, inline=False)
    await ctx.send(embed=embed)


async def daily_task():
    servers_ = db.all_servers(False)
    guilds = client.guilds
    for guild in guilds:
        is_in = True
        repeated = 0
        for server in servers_:
            if guild.id == server[1]:
                repeated += 1
                is_in = False
        if repeated == 2:
            db.server_delete(str(guild.id))
        if is_in:
            db.add_server(str(guild.id))

    await asyncio.sleep(24 * 60 * 60)
    await daily_task()


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(config.token)
