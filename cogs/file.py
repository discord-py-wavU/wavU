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
    def add_song(path, r):
        with open(path, 'wb') as f:
            for chunk in r.iter_content():
                if chunk:
                    f.write(chunk)
        f.close()

    @staticmethod
    def create_folder(ctx, arg):
        if arg is not None:
            new_path = config.path + "/" + str(ctx.message.guild.id) + "/" + str(ctx.message.mentions[0].id)
        else:
            new_path = config.path + "/" + str(ctx.message.guild.id)
        if not os.path.exists(new_path):
            os.makedirs(new_path)

    @staticmethod
    def set_path(ctx, arg, msg):
        if arg is not None:
            path = ('audio/' + str(ctx.message.guild.id) + '/' +
                    str(ctx.message.mentions[0].id) + '/' + msg.attachments[0].filename)
            mov = 'audio/' + str(ctx.message.guild.id) + '/' + str(ctx.message.mentions[0].id)
            filename = str(ctx.message.guild.id) + "/" + str(ctx.message.mentions[0].id)
        else:
            path = 'audio/' + str(ctx.message.guild.id) + '/' + msg.attachments[0].filename
            mov = 'audio/' + str(ctx.message.guild.id)
            filename = str(ctx.message.guild.id)

        return path, mov, filename

    @staticmethod
    def required_role(ctx):
        has_role = True
        if "FM" not in (roles.name for roles in ctx.message.author.roles):
            has_role = False

        return has_role

    @commands.command(aliases=['a', 'Add'])
    async def add(self, ctx, arg=None):

        has_role = self.required_role(ctx)

        if not has_role:
            await ctx.send("You need _**FM**_ role to use this command.\nOnly members who have "
                           + "administrator permissions are able to assign _**FM**_ role."
                           + "\nCommand: \"**" + config.prefix + "role @mention**\"")
            return

        loop = self.client.loop or asyncio.get_event_loop()
        await ctx.send("Upload a **.mp3** file or **cancel**", delete_after=30)

        self.create_folder(ctx, arg)

        def check(m):
            return (m.content == "cancel" or m.content == "Cancel" or m.attachments) \
                   and m.author.guild.name == ctx.message.guild.name

        try:
            msg = await self.client.wait_for('message', check=check, timeout=30)

            if msg.content == "cancel" or msg.content == "Cancel":
                await ctx.send('Nothing has been _**added**_')
                await asyncio.sleep(30)
                await msg.delete()
                return

            headers = {
                'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
            }

            path, mov, filename = self.set_path(ctx, arg, msg)

            request_msg = requests.get(msg.attachments[0].url, headers=headers, stream=True)

            mp3 = msg.attachments[0].filename.split('.')
            if mp3[len(mp3) - 1] == "mp3":
                async with ctx.typing():
                    fn = functools.partial(self.add_song, path, request_msg)
                    await loop.run_in_executor(None, fn)
                if arg is not None:
                    await ctx.send('**' + msg.attachments[0].filename + "** has been added to **"
                                   + ctx.message.guild.name + '/' + str(ctx.message.mentions[0]) + '**')
                else:
                    await ctx.send('**' + msg.attachments[0].filename +
                                   "** has been added to **" + ctx.message.guild.name + '**')
            else:
                await ctx.send("This is not a _**.mp3**_ file", delete_after=15)
            await asyncio.sleep(15)
            await msg.delete()

        except asyncio.TimeoutError:
            await ctx.send('Timeout!', delete_after=15)
            await asyncio.sleep(15)
            await ctx.message.delete()

    @staticmethod
    def unzip_songs(filename, path, r):

        with open('audio/' + filename + '.zip', 'wb') as f:
            for chunk in r.iter_content():
                if chunk:
                    f.write(chunk)
        f.close()

        is_valid = True

        with zipfile.ZipFile('audio/' + filename + '.zip', 'r') as zip_ref:
            songs = zip_ref.namelist()

            for song in songs:
                mp3 = song.split('.')
                if mp3[len(mp3) - 1] != "mp3":
                    is_valid = False

            if is_valid:
                zip_ref.extractall(path)
                zip_ref.close()

        return is_valid

    @commands.command(alieses=['Unzip'])
    async def unzip(self, ctx, arg=None):

        has_role = self.required_role(ctx)

        if not has_role:
            await ctx.send("You need _**FM**_ role to use this command.\nOnly members who have "
                           + "administrator permissions are able to assign _**FM**_ role."
                           + "\nCommand: \"**" + config.prefix + "role @mention**\"")
            return

        loop = self.client.loop or asyncio.get_event_loop()
        await ctx.send("Upload a **.zip** file or **cancel**", delete_after=30)
        self.create_folder(ctx, arg)

        def check(m):
            return (m.content == "cancel" or m.content == "Cancel" or m.attachments) \
                   and m.author.guild.name == ctx.message.guild.name

        try:
            msg = await self.client.wait_for('message', check=check, timeout=30)

            if msg.content == "cancel" or msg.content == "Cancel":
                await ctx.send('Nothing has been _**unzipped**_')
                await asyncio.sleep(30)
                await msg.delete()
                return

            headers = {
                'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
            }

            path, mov, filename = self.set_path(ctx, arg, msg)

            r = requests.get(msg.attachments[0].url, headers=headers, stream=True)

            async with ctx.typing():
                fn = functools.partial(self.unzip_songs, filename, path, r)
                is_valid = await loop.run_in_executor(None, fn)

            if is_valid:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        move(root + '/' + file, mov + '/' + file)

                os.rmdir(path)
                os.remove('audio/' + filename + '.zip')

                await ctx.send('**' + msg.attachments[0].filename + '** was added to **' + filename + '**')
                await asyncio.sleep(30)
                await msg.delete()
            else:
                os.remove('audio/' + filename + '.zip')
                await ctx.send(msg.attachments[0].filename + ' was not a valid _**.zip**_ file')
                await asyncio.sleep(30)
                await msg.delete()

        except asyncio.TimeoutError:
            await ctx.send('Timeout!', delete_after=15)
            await asyncio.sleep(15)
            await ctx.message.delete()

    @staticmethod
    def get_path(ctx, arg):
        if arg is not None:
            path = config.path + '/' + str(ctx.message.guild.id) + "/" + str(ctx.message.mentions[0].id)
        else:
            path = config.path + "/" + str(ctx.message.guild.id)

        return path

    @staticmethod
    def get_list_songs(path):
        try:
            songs = [song for song in listdir(path) if isfile(join(path, song)) and '.mp3' in song]
        except Exception as e:
            print(str(e))
            songs = []

        return songs

    @commands.command(aliases=['Delete', 'del', 'Del', 'remove', 'Remove', 'rm', 'Rm', 'RM'])
    async def delete(self, ctx, arg=None):

        has_role = self.required_role(ctx)
        if not has_role:
            await ctx.send("You need _**FM**_ role to use this command.\nOnly members who have "
                           + "administrator permissions are able to assign _**FM**_ role."
                           + "\nCommand: \"**" + config.prefix + "role @mention**\"")
            return

        path = self.get_path(ctx, arg)

        songs = self.get_list_songs(path)

        if songs:

            list_songs = ""
            for index, song in enumerate(songs):
                list_songs = list_songs + str(index + 1) + ". " + song.split(".mp3")[0] + "\n"
            list_songs = list_songs + "**all**\n**cancel**"
            await ctx.send("List .mp3 files:\n" + list_songs, delete_after=30)

            await ctx.send("Choose a _number_ to delete a _**.mp3**_ file", delete_after=30)

            def check(m):
                return (m.content.isdigit() and m.author.guild.name == ctx.message.guild.name) \
                       or m.content == "cancel" or m.content == "Cancel" or m.content == "all" \
                       or m.content == "All"

            try:
                for i in range(3):
                    msg = await self.client.wait_for('message', check=check, timeout=30)
                    if msg.content.isdigit() and int(msg.content) <= len(songs) and int(msg.content) != 0:
                        os.remove(path + '/' + songs[int(msg.content) - 1])
                        await ctx.send('**' + songs[int(msg.content) - 1] + '** has been _**deleted**_')
                        break
                    elif msg.content == "cancel" or msg.content == "Cancel":
                        await ctx.send("Nothing has been _**deleted**_")
                        await msg.delete()
                        break
                    elif msg.content == "all" or msg.content == "All":
                        for index in range(len(songs)):
                            os.remove(path + '/' + songs[index])
                        await ctx.send('All the _**.mp3**_ files has been _**deleted**_')
                        await msg.delete()
                        break
                    elif int(msg.content) > len(songs) or int(msg.content) == 0:
                        await ctx.send("That number is not an option. Try again **(" + str(i + 1) + "/3)**",
                                       delete_after=10)
                        if i == 2:
                            await ctx.send("None of the attempts were correct, _**delete**_ has been aborted")
                    await msg.delete()

            except asyncio.TimeoutError:
                await ctx.send('Timeout!', delete_after=15)
                await asyncio.sleep(15)
                await ctx.message.delete()
        else:
            await ctx.send('_List is empty_')

    @commands.command(aliases=['Edit'])
    async def edit(self, ctx, arg=None):

        has_role = self.required_role(ctx)
        if not has_role:
            await ctx.send("You need _**FM**_ role to use this command.\nOnly members who have "
                           + "administrator permissions are able to assign _**FM**_ role."
                           + "\nCommand: \"**" + config.prefix + "role @mention**\"")
            return

        path = self.get_path(ctx, arg)

        songs = self.get_list_songs(path)

        if songs:

            list_songs = ""
            for index, song in enumerate(songs):
                list_songs = list_songs + str(index + 1) + ". " + song.split(".mp3")[0] + "\n"
            list_songs = list_songs + "**cancel**"
            await ctx.send("List .mp3 files:\n" + list_songs, delete_after=30)
            await ctx.send("Choose a _number_ to edit a _**.mp3**_ file _name_", delete_after=30)

            def check_number(m):
                return (m.content.isdigit() and m.author.guild.name == ctx.message.guild.name) \
                       or m.content == "cancel" or m.content == "Cancel" or m.content == "all" \
                       or m.content == "All"

            def check_name(m):
                return m.author.guild.name == ctx.message.guild.name \
                       or m.content == "cancel" or m.content == "Cancel"

            try:
                for i in range(3):

                    msg = await self.client.wait_for('message', check=check_number, timeout=30)

                    if msg.content.isdigit() and int(msg.content) <= len(songs) and int(msg.content) != 0:

                        await ctx.send("Choose a new _name_ or type _**cancel**_ to not edit", delete_after=60)
                        msg_edit = await self.client.wait_for('message', check=check_name, timeout=60)

                        if msg_edit.content == 'cancel' or msg_edit.content == 'Cancel':
                            await ctx.send("Nothing has been _**edited**_")
                            await asyncio.sleep(10)
                            await msg.delete()
                        else:
                            os.rename(path + '/' + songs[int(msg.content) - 1],
                                      path + '/' + msg_edit.content + '.mp3')
                            await ctx.send('**' + songs[int(msg.content) - 1] +
                                           '** has been edited to **' + msg_edit.content + '.mp3**')
                        await msg_edit.delete()
                        break
                    elif msg.content == "cancel" or msg.content == "Cancel":
                        await ctx.send("Nothing has been _**edited**_")
                        await msg.delete()
                        break
                    elif int(msg.content) > len(songs) or int(msg.content) == 0:
                        await ctx.send("That number is not an option. Try again **(" + str(i + 1) + "/3)**",
                                       delete_after=10)
                        if i == 2:
                            await ctx.send("None of the attempts were correct, _**edit**_ has been aborted")
                    await msg.delete()
            except asyncio.TimeoutError:
                await ctx.send('Timeout!', delete_after=15)
                await asyncio.sleep(15)
                await ctx.message.delete()
        else:
            await ctx.send('_List is empty_')

    @commands.command(name='list', aliases=['show', 'List', 'Show'])
    async def show_list(self, ctx, arg=None):

        path = self.get_path(ctx, arg)

        songs = self.get_list_songs(path)

        if songs:
            list_songs = ""
            for index, song in enumerate(songs):
                list_songs = list_songs + str(index + 1) + ". " + song.split(".mp3")[0] + "\n"
            await ctx.send("List .mp3 files:\n" + list_songs, delete_after=60)
        else:
            await ctx.send('_List is empty_')

    @staticmethod
    def zipping(file_path, path):
        file_zip = zipfile.ZipFile('audio/' + file_path + '.zip', 'w', zipfile.ZIP_DEFLATED)
        is_empty = False

        for root, dirs, files in os.walk(path):
            if not files and root == path:
                is_empty = True
                break
            else:
                for file in files:
                    song = file.split('.')
                    if song[len(song) - 1] == "mp3" and root == path:
                        file_zip.write(os.path.join(root, file),
                                       os.path.relpath(os.path.join(root + '/' + file_path, file),
                                                       os.path.join(path, file_path)))

        file_zip.close()

        return is_empty

    @commands.command(aliases=['Zip', 'z', 'Z'])
    async def zip(self, ctx, arg=None):

        has_role = self.required_role(ctx)

        if not has_role:
            await ctx.send("You need _**FM**_ role to use this command.\nOnly members who have "
                           + "administrator permissions are able to assign _**FM**_ role."
                           + "\nCommand: \"**" + config.prefix + "role @mention**\"")
            return

        loop = self.client.loop or asyncio.get_event_loop()
        if arg is not None:
            path = config.path + "/" + str(ctx.message.guild.id) + "/" + str(ctx.message.mentions[0].id)
            filename = ctx.message.guild.name + "/" + str(ctx.message.mentions[0])
            file_path = str(ctx.message.guild.id) + "/" + str(ctx.message.mentions[0].id)
        else:
            path = config.path + "/" + str(ctx.message.guild.id)
            filename = ctx.message.guild.name
            file_path = str(ctx.message.guild.id)

        async with ctx.typing():
            fn = functools.partial(self.zipping, file_path, path)
            is_empty = await loop.run_in_executor(None, fn)

        if not is_empty:
            await ctx.send(file=discord.File(fp='audio/' + file_path + '.zip', filename=filename + '.zip'))
            os.remove(config.path + '/' + file_path + '.zip')
        else:
            await ctx.send("There's no file to add to _**zip**_")


def setup(client):
    client.add_cog(FileManagement(client))
