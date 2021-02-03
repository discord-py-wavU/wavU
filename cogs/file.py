from discord.ext import commands
import discord

import os
import requests
import config
import asyncio
import functools

from shutil import move

from os import listdir
from os.path import isfile, join
import zipfile


class FileManagement(commands.Cog):

    def __init__(self, client):
        self.client = client

    @staticmethod
    def unzip(filename, path, r):

        with open('audio/' + filename + '.zip', 'wb') as f:
            for chunk in r.iter_content():
                if chunk:
                    f.write(chunk)
        f.close()

        isValid = True

        with zipfile.ZipFile('audio/' + filename + '.zip', 'r') as zip_ref:
            songs = zip_ref.namelist()

            for song in songs:
                mp3 = song.split('.')
                if mp3[len(mp3) - 1] != "mp3":
                    print(song)
                    isValid = False

            if isValid:
                zip_ref.extractall(path)
                zip_ref.close()

        return isValid

    @staticmethod
    def add_song(path, r):
        with open(path, 'wb') as f:
            for chunk in r.iter_content():
                if chunk:
                    f.write(chunk)
        f.close()

    @commands.command(aliases=['a', 'unzip'], help='Add one .mp3 file')
    @commands.has_role('PepeMaster')
    async def add(self, ctx, arg=None):
        loop = self.client.loop or asyncio.get_event_loop()
        if str(ctx.message.content).split(' ')[0] == config.prefix + 'unzip':
            await ctx.send("Upload a .zip file", delete_after=30)
        else:
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

            if arg is not None:
                path = ('audio/' + ctx.message.guild.name + '/' +
                        str(ctx.message.mentions[0]) + '/' + msg.attachments[0].filename)
                mov = 'audio/' + ctx.message.guild.name + '/' + str(ctx.message.mentions[0])
                filename = ctx.message.guild.name + "/" + str(ctx.message.mentions[0])
            else:
                path = 'audio/' + ctx.message.guild.name + '/' + msg.attachments[0].filename
                mov = 'audio/' + ctx.message.guild.name
                filename = ctx.message.guild.name

            r = requests.get(msg.attachments[0].url, headers=headers, stream=True)

            if str(ctx.message.content).split(' ')[0] == config.prefix + 'unzip':

                async with ctx.typing():
                    fn = functools.partial(self.unzip, filename, path, r)
                    isValid = await loop.run_in_executor(None, fn)

                if isValid:
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            move(root + '/' + file, mov + '/' + file)

                    os.rmdir(path)
                    os.remove('audio/' + filename + '.zip')

                    await ctx.send(msg.attachments[0].filename + ' was added to ' + filename)
                    await asyncio.sleep(30)
                    await msg.delete()
                else:
                    os.remove('audio/' + filename + '.zip')
                    await ctx.send(msg.attachments[0].filename + ' was not a valid .zip file')
                    await asyncio.sleep(30)
                    await msg.delete()

            else:
                mp3 = msg.attachments[0].filename.split('.')
                if mp3[len(mp3) - 1] == "mp3":
                    async with ctx.typing():
                        fn = functools.partial(self.add_song, path, r)
                        await loop.run_in_executor(None, fn)
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

    @commands.command(aliases=['dlt', 'd', 'del', 'edit'], help='Delete one chosen .mp3 file')
    @commands.has_role('PepeMaster')
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
                list_songs = list_songs + str(index + 1) + ". " + song.split(".mp3")[0] + "\n"
            if ctx.message.content == config.prefix + 'edit':
                list_songs = list_songs + "cancel"
            else:
                list_songs = list_songs + "Type all to delete all the .mp3 files\ncancel"
            await ctx.send("List .mp3 files:\n" + list_songs, delete_after=30)
            if ctx.message.content == config.prefix + 'edit':
                await ctx.send("Choose a number to edit a .mp3 file name", delete_after=30)
            else:
                await ctx.send("Choose a number to delete a .mp3 file", delete_after=30)

            def check_delete(m):
                return (m.content.isdigit() and m.author.guild.name == ctx.message.guild.name) \
                       or m.content == "cancel" or m.content == "Cancel" or m.content == "all" \
                       or m.content == "All"

            def check_edit(m):
                return m.author.guild.name == ctx.message.guild.name \
                       or m.content == "cancel" or m.content == "Cancel"

            try:
                for i in range(3):
                    msg = await self.client.wait_for('message', check=check_delete, timeout=30)
                    if msg.content.isdigit() and int(msg.content) <= len(songs) and int(msg.content) != 0:
                        if ctx.message.content == config.prefix + 'edit':
                            await ctx.send("Choose a new name or type Cancel to not edit", delete_after=60)
                            msg_edit = await self.client.wait_for('message', check=check_edit, timeout=60)
                            if msg_edit.content == 'cancel' or msg_edit.content == 'Cancel':
                                await ctx.send("Nothing has been edited")
                                await asyncio.sleep(10)
                                await msg.delete()
                            else:
                                os.rename(path + '/' + songs[int(msg.content) - 1],
                                          path + '/' + msg_edit.content + '.mp3')
                                await ctx.send(songs[int(msg.content) - 1] +
                                               ' has been edited to ' + msg_edit.content + '.mp3')
                            break
                            await msg_edit.delete()
                        else:
                            os.remove(path + '/' + songs[int(msg.content) - 1])
                            await ctx.send(songs[int(msg.content) - 1] + ' has been deleted')
                        break
                    elif msg.content == "cancel" or msg.content == "Cancel":
                        if ctx.message.content == config.prefix + 'edit':
                            await ctx.send("Nothing has been edited")
                        else:
                            await ctx.send("Nothing has been deleted")
                        await msg.delete()
                        break
                    elif msg.content == "all" or msg.content == "All":
                        for i in range(len(songs)):
                            os.remove(path + '/' + songs[i])
                        await ctx.send('All the .mp3 files has been deleted')
                        await msg.delete()
                        break
                    elif int(msg.content) > len(songs) or int(msg.content) == 0:
                        await ctx.send("That number is not an option. Try again ("+str(i+1)+"/3)", delete_after=10)
                        if i == 2:
                            if ctx.message.content == config.prefix + 'edit':
                                await ctx.send("None of the attempts were correct, edit has been aborted")
                            else:
                                await ctx.send("None of the attempts were correct, delete has been aborted")
                    await msg.delete()

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
                list_songs = list_songs + str(index + 1) + ". " + song.split(".mp3")[0] + "\n"
            await ctx.send("List .mp3 files:\n" + list_songs, delete_after=60)
        else:
            await ctx.send('List is empty')

    @staticmethod
    def zipping(filename, path):
        zip = zipfile.ZipFile('audio/' + filename + '.zip', 'w', zipfile.ZIP_DEFLATED)
        isEmpty = False

        for root, dirs, files in os.walk(path):
            if not files and root == path:
                isEmpty = True
                break
            else:
                for file in files:
                    song = file.split('.')
                    if song[len(song) - 1] == "mp3" and root == path:
                        zip.write(os.path.join(root, file),
                                  os.path.relpath(os.path.join(root + '/' + filename, file),
                                                  os.path.join(path, filename)))

        zip.close()

        return isEmpty

    @commands.command()
    @commands.has_role('PepeMaster')
    async def zip(self, ctx, arg=None):
        loop = self.client.loop or asyncio.get_event_loop()
        if arg is not None:
            path = config.path + "/" + ctx.message.guild.name + "/" + str(ctx.message.mentions[0])
            filename = ctx.message.guild.name + "/" + str(ctx.message.mentions[0])
        else:
            path = config.path + "/" + ctx.message.guild.name
            filename = ctx.message.guild.name

        async with ctx.typing():
            fn = functools.partial(self.zipping, filename, path)
            isEmpty = await loop.run_in_executor(None, fn)

        if not isEmpty:
            await ctx.send(file=discord.File(fp='audio/' + filename + '.zip', filename=filename + '.zip'))
            os.remove(config.path + '/' + filename + '.zip')
        else:
            await ctx.send("There's no song in the zip file")


def setup(client):
    client.add_cog(FileManagement(client))
