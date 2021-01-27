from discord.ext import commands

import os
import requests
import config
import asyncio

from os import listdir
from os.path import isfile, join


class FileManagement(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['a'], help='Add one .mp3 file')
    async def add(self, ctx, arg=None):

        await ctx.send("Upload a .mp3 file", delete_after=30)
        if arg is not None:
            new_path = config.path + "/" + ctx.message.guild.name + "/" + str(ctx.message.mentions[0])
        else:
            new_path = config.path + "/" + ctx.message.guild.name
        if not os.path.exists(new_path):
            os.makedirs(new_path)

        def check(m):
            return m.attachments and m.author.guild.name == ctx.message.guild.name

        try:
            msg = await self.client.wait_for('message', check=check, timeout=30)

            headers = {
                'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
            }

            r = requests.get(msg.attachments[0].url, headers=headers, stream=True)
            mp3 = msg.attachments[0].filename.split('.')
            if arg is not None:
                path = ('audio/' + ctx.message.guild.name + '/' +
                        str(ctx.message.mentions[0]) + '/' + msg.attachments[0].filename)
            else:
                path = 'audio/' + ctx.message.guild.name + '/' + msg.attachments[0].filename

            if mp3[len(mp3) - 1] == "mp3":
                with open(path, 'wb') as f:
                    for chunk in r.iter_content():
                        if chunk:
                            f.write(chunk)
                f.close()
                if arg is not None:
                    await ctx.send(msg.attachments[0].filename + " has been added to "
                                   + ctx.message.guild.name + '/' + str(ctx.message.mentions[0]))
                else:
                    await ctx.send(msg.attachments[0].filename + " has been added to " + ctx.message.guild.name)
            else:
                await ctx.send("This is not a .mp3 file", delete_after=15)
            await asyncio.sleep(15)
            await msg.delete()

        except asyncio.TimeoutError:
            await ctx.send('Timeout!', delete_after=15)
            await asyncio.sleep(15)
            await ctx.message.delete()

    @commands.command(aliases=['dlt', 'd', 'del'], help='Delete one chosen .mp3 file')
    async def delete(self, ctx, arg=None):
        if arg is not None:
            path = config.path + '/' + ctx.message.guild.name + "/" + str(ctx.message.mentions[0])
        else:
            path = config.path + "/" + ctx.message.guild.name
        try:
            songs = [f for f in listdir(path) if isfile(join(path, f)) and '.mp3' in f]
        except Exception as e:
            print(str(e))
            songs = []

        if songs:

            list_songs = ""
            for index, song in enumerate(songs):
                list_songs = list_songs + str(index + 1) + ". " + song + "\n"
            list_songs = list_songs + "cancel"
            await ctx.send("List .mp3 files:\n" + list_songs, delete_after=30)

            await ctx.send("Choose a number to delete a .mp3 file", delete_after=30)

            def check(m):
                return (m.content.isdigit() and m.author.guild.name == ctx.message.guild.name) \
                       or m.content == "cancel" or m.content == "Cancel"

            try:
                msg = await self.client.wait_for('message', check=check, timeout=30)

                if msg.content.isdigit() and int(msg.content) <= len(songs) and int(msg.content) != 0:
                    os.remove(path + '/' + songs[int(msg.content) - 1])
                    await ctx.send(songs[int(msg.content) - 1] + ' has been deleted')
                elif msg.content == "cancel" or msg.content == "Cancel":
                    await ctx.send("Nothing has been deleted")
                elif int(msg.content) > len(songs) or int(msg.content) == 0:
                    await ctx.send("That number is not an option")
            except asyncio.TimeoutError:
                await ctx.send('Timeout!', delete_after=15)
                await asyncio.sleep(15)
                await ctx.message.delete()
        else:
            await ctx.send('List is empty')

    @commands.command(name='list', aliases=['show'], help="Show list of .mp3 files")
    async def show_list(self, ctx, arg=None):
        if arg is not None:
            path = config.path + '/' + ctx.message.guild.name + '/' + str(ctx.message.mentions[0])
        else:
            path = config.path + "/" + ctx.message.guild.name
        try:
            songs = [f for f in listdir(path) if isfile(join(path, f)) and '.mp3' in f]
        except Exception as e:
            print(str(e))
            songs = []

        if songs:
            list_songs = ""
            for index, song in enumerate(songs):
                list_songs = list_songs + str(index + 1) + ". " + song + "\n"
            await ctx.send("List .mp3 files:\n" + list_songs, delete_after=30)
        else:
            await ctx.send('List is empty')


def setup(client):
    client.add_cog(FileManagement(client))
