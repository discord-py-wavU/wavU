import discord
from discord.ext import commands

import os
import requests
import config

from os import listdir
from os.path import isfile, join

class FileManagement(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def add(self, ctx, arg = None):

        await ctx.send("Update a .mp3 file", delete_after=30)
        if arg != None:
            newpath = config.path + "/" + ctx.message.guild.name + "/" + str(ctx.message.mentions[0])
        else:
            newpath = config.path + "/" + ctx.message.guild.name
        if not os.path.exists(newpath):
            os.makedirs(newpath)

        def check(m):
            return m.attachments
        msg = await self.client.wait_for('message', check=check)

        headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
        }

        r = requests.get(msg.attachments[0].url, headers=headers, stream=True)
        mp3 = msg.attachments[0].filename.split('.')
        if arg != None:
            path = 'audio/' + ctx.message.guild.name + '/' + str(ctx.message.mentions[0]) + '/' + msg.attachments[0].filename
        else:
            path = 'audio/' + ctx.message.guild.name + '/' + msg.attachments[0].filename

        if mp3[len(mp3)-1] == "mp3":
            with open(path, 'wb') as f:
                for chunk in r.iter_content():
                    if chunk:
                        f.write(chunk)
            f.close()
        else:
            await ctx.send("This is not a .mp3 file")


    @commands.command()
    async def delete(self, ctx, arg=None):
        if arg != None:
            path = config.path + '/' + ctx.message.guild.name + "/" + str(ctx.message.mentions[0])
        else:
            path = config.path + "/" + ctx.message.guild.name
        songs = [f for f in listdir(path) if isfile(join(path, f)) and '.mp3' in f]
        listsongs = ""
        for index, song in enumerate(songs):
            listsongs = listsongs + str(index+1) + ". " + song + "\n" 
        listsongs = listsongs + "cancel"
        await ctx.send("List .mp3 files:\n" + listsongs)

        await ctx.send("Choose a number to delete a .mp3 file")

        def check(m):
            return m.content.isdigit() or m.content == "cancel" or m.content == "Cancel"
        msg = await self.client.wait_for('message', check=check, timeout= 45)

        if msg.content.isdigit() and int(msg.content) <= len(songs) and int(msg.content) != 0:
            os.remove(path + '/' + songs[int(msg.content)-1])
            await ctx.send(songs[int(msg.content)-1] + ' has been deleted')
        elif msg.content == "cancel" or msg.content == "Cancel":
            await ctx.send("Nothing has been deleted")
        elif int(msg.content) > len(songs) or int(msg.content) == 0:
            await ctx.send("That number is not an option")

    @commands.command(name='list', aliases=['show'])
    async def show_list(self, ctx, arg=None):
        if arg != None:
            path = config.path + '/' + ctx.message.guild.name + '/' + str(ctx.message.mentions[0])
        else:
            path = config.path + "/" + ctx.message.guild.name
        songs = [f for f in listdir(path) if isfile(join(path, f)) and '.mp3' in f]
        listsongs = ""
        for index, song in enumerate(songs):
            listsongs = listsongs + str(index+1) + ". " + song + "\n" 
        await ctx.send("List .mp3 files:\n" + listsongs)


def setup(client):
    client.add_cog(FileManagement(client))