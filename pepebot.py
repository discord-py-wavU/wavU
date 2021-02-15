import os
import discord
from cogs import db
from discord.ext import commands
import discord.utils
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
        if channel.permissions_for(guild.me).administrator:
            channel = await guild.create_text_channel('wavU')
            await channel.send(
                "Thanks for adding me to your server!\nHere is my website to know more about my commands\n"
                + "{URL}\nAnd here is my personal discord server if you want to be part of this community\n"
                + "{discord server link})

            await guild.create_role(name='FM', reason="necessary to control bot's commands", mentionable=False)

            db.add_server(str(guild.name))
        break


@client.command()
async def role(ctx, arg=None):
    role = discord.utils.get(ctx.guild.roles, name="FM")

    if ctx.message.author.guild_permissions.administrator:
        if arg is None or not ctx.message.mentions:
            await ctx.send("You need to mention who you want to give _**FM**_ role")
        else:
            if "FM" in (roles.name for roles in ctx.message.mentions[0].roles):
                await ctx.send("This person already has FM role")
            else:
                await ctx.message.mentions[0].add_roles(role)
                await ctx.send("_**" + str(ctx.message.mentions[0]) + "**_ has _File Manager_ role")
    else:
        await ctx.send("You need to have administrator permissions to assign FM role")

@client.command()
async def unrole(ctx, arg=None):
    role = discord.utils.get(ctx.guild.roles, name="FM")

    if ctx.message.author.guild_permissions.administrator:
        if arg is None or not ctx.message.mentions:
            await ctx.send("You need to mention who you want to remove _**FM**_ role")
        else:
            if "FM" in (roles.name for roles in ctx.message.mentions[0].roles):
                await ctx.message.mentions[0].remove_roles(role)
                await ctx.send("_**" + str(ctx.message.mentions[0]) + "**_ has been removed from _File Manager_ role")
            else:
                await ctx.send("This person hasn't FM role")
    else:
        await ctx.send("You need to have administrator permissions to remove FM role")


@client.event
async def on_guild_remove(guild):
    db.server_delete(str(guild.name))


async def daily_task():
    servers = db.all_servers(False)
    guilds = client.guilds
    for guild in guilds:
        is_in = True
        repeated = 0
        for server in servers:
            if guild.name == server[1]:
                repeated += 1
                is_in = False
        if repeated == 2:
            db.server_delete(str(guild.name))
        if is_in:
            db.add_server(str(guild.name))

    await asyncio.sleep(24*60*60)
    await daily_task()


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(config.token)
