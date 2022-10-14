import asyncio
import logging
import os
import shutil
from os import listdir
from os.path import isfile, join
from shutil import copy

import discord
import discord.utils
from discord.ext import commands

import content
from resources.bot.mods import db


class Management(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['Role'])
    async def role(self, ctx, arg=None):
        roles = discord.utils.get(ctx.guild.roles, name="FM")

        if ctx.message.author.guild_permissions.administrator:
            if arg is None or not ctx.message.mentions:
                await ctx.send("You need to mention who you want to give _**FM**_ role")
            else:
                if "FM" in (roles.name for roles in ctx.message.mentions[0].roles):
                    await ctx.send("This person already has FM role")
                else:
                    await ctx.message.mentions[0].add_roles(roles)
                    await ctx.send("_**" + str(ctx.message.mentions[0]) + "**_ has _File Manager_ role")
        else:
            await ctx.send("You need to have administrator permissions to assign FM role")

    @commands.command(aliases=['Unrole'])
    async def unrole(self, ctx, arg=None):
        roles = discord.utils.get(ctx.guild.roles, name="FM")

        if ctx.message.author.guild_permissions.administrator:
            if arg is None or not ctx.message.mentions:
                await ctx.send("You need to mention who you want to remove _**FM**_ role")
            else:
                if "FM" in (roles.name for roles in ctx.message.mentions[0].roles):
                    await ctx.message.mentions[0].remove_roles(roles)
                    await ctx.send(
                        "_**" + str(ctx.message.mentions[0]) + "**_ has been removed from _File Manager_ role")
                else:
                    await ctx.send("This person hasn't FM role")
        else:
            await ctx.send("You need to have administrator permissions to remove FM role")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).administrator:
                owner = await self.client.fetch_user(guild.owner_id)
                await owner.send(
                    "Thanks for adding me to your server!\n"
                    "Here is my personal discord server if you want to be part of this community\n"
                    + content.server_link)

                await guild.create_role(name='FM', reason="necessary to control bot's commands", mentionable=True)

                # ADD SERVER TO DB

                # ADD default audios to new server

                default_songs_path = config.path + '/default_audios/'
                path = config.path + "/" + str(guild.id)
                if not os.path.exists(path):
                    os.makedirs(path)
                songs = [f for f in listdir(default_songs_path) if isfile(join(default_songs_path, f)) and '.mp3' in f]
                for song in songs:
                    copy(default_songs_path + song, path)

                db.add_server(guild.id)
            break

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):

        # UNASSIGN ALL AUDIOS FROM DB

        logging.info(f'The server {guild.name} was removed')
        path = config.path + '/' + str(guild.id)
        shutil.rmtree(path)
        db.server_delete(guild.id, None)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        logging.info(f'The server {member.guild.name} was joined')
        await member.send(f"Welcome to **{member.guild.name}**, i'm wavU and i'll appear on *Voice channels* "
                          "everytime someone joins in and play any random audio this server has. To know more "
                          "about me, type **=help**. Have a nice day!")

        await asyncio.sleep(3 * 60 * 60)

        msgs = member.dm_channel
        async for msg in msgs.history(limit=10):
            if msg.author == self.client.user:
                await msg.delete()


def setup(client):
    client.add_cog(Management(client))