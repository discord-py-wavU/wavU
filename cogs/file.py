import asyncio
import functools
import os
import zipfile
from datetime import datetime
from os import listdir
from os.path import isfile, join
from shutil import move

import discord
import mutagen
import requests
from discord.ext import commands

import config


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
    async def create_folder(ctx, arg):
        valid = True
        all_channel = ctx.message.guild.voice_channels
        name_channel = [channel.name for channel in all_channel]
        if arg in [channel.name for channel in all_channel]:
            s_channel = all_channel[name_channel.index(arg)]
            new_path = config.path + "/" + str(ctx.message.guild.id) + "/" + str(s_channel.id)
        elif ctx.message.mentions:
            new_path = config.path + "/" + str(ctx.message.guild.id) + "/" + str(ctx.message.mentions[0].id)
        elif arg is None:
            new_path = config.path + "/" + str(ctx.message.guild.id)
        else:
            await ctx.send('No valid argument, please try again.\n'
                           "If your channel's name has spaces you need to use quotes\n"
                           'ex.: "Channel with spaces"'
                           '\nType **' + config.prefix + 'help** for more information')
            valid = False
            new_path = None

        if valid and not os.path.exists(new_path):
            os.makedirs(new_path)

        return valid

    @staticmethod
    def set_path(ctx, arg, msg):
        all_channel = ctx.message.guild.voice_channels
        name_channel = [channel.name for channel in all_channel]
        if arg in [channel.name for channel in all_channel]:
            s_channel = all_channel[name_channel.index(arg)]
            path = 'audio/' + str(ctx.message.guild.id) + "/" + str(s_channel.id) + '/' + msg.attachments[0].filename
            mov = 'audio/' + str(ctx.message.guild.id) + '/' + str(s_channel.id)
            file_path = str(ctx.message.guild.id) + "/" + str(s_channel.id)
            filename = ctx.message.guild.name + "/" + s_channel.name
        elif arg is not None:
            path = ('audio/' + str(ctx.message.guild.id) + '/' +
                    str(ctx.message.mentions[0].id) + '/' + msg.attachments[0].filename)
            mov = 'audio/' + str(ctx.message.guild.id) + '/' + str(ctx.message.mentions[0].id)
            file_path = str(ctx.message.guild.id) + "/" + str(ctx.message.mentions[0].id)
            filename = ctx.message.guild.name + "/" + str(ctx.message.mentions[0])
        else:
            path = 'audio/' + str(ctx.message.guild.id) + '/' + msg.attachments[0].filename
            mov = 'audio/' + str(ctx.message.guild.id)
            file_path = str(ctx.message.guild.id)
            filename = ctx.message.guild.name

        return path, mov, filename, file_path

    @staticmethod
    async def required_role(ctx):
        has_role = True
        if "FM" not in (roles.name for roles in ctx.message.author.roles):
            await ctx.send("You need _**FM**_ role to use this command.\nOnly members who have "
                           + "administrator permissions are able to assign _**FM**_ role."
                           + "\nCommand: \"**" + config.prefix + "role @mention**\"")
            has_role = False

        return has_role

    @commands.command(aliases=['a', 'Add'])
    async def add(self, ctx, arg=None):

        has_role = await self.required_role(ctx)

        if not has_role:
            return

        loop = self.client.loop or asyncio.get_event_loop()
        valid = await self.create_folder(ctx, arg)

        if not valid:
            return

        await ctx.send("Upload a **.mp3** file or **cancel**", delete_after=30)

        def check(m):
            return (m.content == "cancel" or m.content == "Cancel" or m.attachments) \
                   and m.author.guild.id == ctx.message.guild.id

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

            path, mov, filename, file_path = self.set_path(ctx, arg, msg)

            request_msg = requests.get(msg.attachments[0].url, headers=headers, stream=False)

            mp3 = msg.attachments[0].filename.split('.')
            if mp3[len(mp3) - 1] == "mp3":
                async with ctx.typing():
                    fn = functools.partial(self.add_song, path, request_msg)
                    await loop.run_in_executor(None, fn)

                path = config.path + '/' + file_path + '/' + msg.attachments[0].filename
                audio = mutagen.File(path)

                if int(audio.info.length) < 10:
                    await ctx.send('**' + msg.attachments[0].filename + '** was added to **' + filename + '**')
                else:
                    await ctx.send('**' + msg.attachments[0].filename + '** is longer than 10 seconds, **add** was '
                                                                        'aborted')
                    os.remove(path)
            else:
                await ctx.send("This is not a _**.mp3**_ file", delete_after=15)
            await asyncio.sleep(15)
            await msg.delete()

        except asyncio.TimeoutError:
            await ctx.send('Timeout!', delete_after=15)
            await asyncio.sleep(15)
            await ctx.message.delete()

    @staticmethod
    def unzip_songs(file_path, path, r, zip_name):

        with open('audio/' + file_path + '.zip', 'wb') as f:
            for chunk in r.iter_content():
                if chunk:
                    f.write(chunk)
        f.close()

        with zipfile.ZipFile('audio/' + file_path + '.zip', 'r') as zip_ref:
            files = zip_ref.namelist()
            valid_files = []
            invalid_files_format = []
            for file in files:
                mp3 = file.split('.')
                if mp3[len(mp3) - 1] != "mp3":
                    invalid_files_format.append(file)
                else:
                    valid_files.append(file)

            invalid_files_duration = []

            if valid_files:
                zip_ref.extractall(path, members=valid_files)
                zip_ref.close()

                for file in valid_files:
                    path = config.path + '/' + file_path + '/' + zip_name + '/' + file
                    audio = mutagen.File(path)
                    d = datetime.fromtimestamp(int(audio.info.length)).strftime("%M:%S")
                    if int(audio.info.length) >= 10:
                        invalid_files_duration.append((file, d))
                        os.remove(path)

                for file in invalid_files_duration:
                    valid_files.remove(file[0])

        return valid_files, invalid_files_format, invalid_files_duration

    @commands.command(aliases=['Unzip'])
    async def unzip(self, ctx, arg=None):

        has_role = await self.required_role(ctx)

        if not has_role:
            return

        loop = self.client.loop or asyncio.get_event_loop()

        valid = await self.create_folder(ctx, arg)

        if not valid:
            return

        await ctx.send("Upload a **.zip** file or **cancel**", delete_after=30)

        def check(m):
            return (m.content == "cancel" or m.content == "Cancel" or m.attachments) \
                   and m.author.guild.id == ctx.message.guild.id

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

            path, mov, filename, file_path = self.set_path(ctx, arg, msg)

            r = requests.get(msg.attachments[0].url, headers=headers, stream=False)
            zip_name = msg.attachments[0].filename

            async with ctx.typing():
                fn = functools.partial(self.unzip_songs, file_path, path, r, zip_name)
                valid_files, invalid_files_format, invalid_files_duration = await loop.run_in_executor(None, fn)

            if valid_files:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        move(root + '/' + file, mov + '/' + file)

                os.rmdir(path)
                os.remove('audio/' + file_path + '.zip')

                valid_text = ""

                for file in valid_files:
                    valid_text = valid_text + ":white_check_mark:" + file + "\n"

                invalid_format_text = ""
                if invalid_files_format:
                    invalid_format_text = "Invalid files format:\n"

                    for file in invalid_files_format:
                        invalid_format_text = invalid_format_text + ":x:" + file + "\n"

                invalid_duration_text = ""
                if invalid_files_duration:
                    invalid_duration_text = "Invalid files duration:\n"

                    for file in invalid_files_duration:
                        invalid_duration_text = invalid_duration_text + ":x:" + file[0] + " " + file[1] + "\n"

                await ctx.send('**' + msg.attachments[0].filename + '** was added to **' + filename + '**\n' +
                               'Valid files:\n' + valid_text + invalid_format_text + invalid_duration_text)
                await asyncio.sleep(30)
                await msg.delete()
            else:
                os.remove('audio/' + file_path + '.zip')
                await ctx.send(msg.attachments[0].filename + ' was not a valid _**.zip**_ file')
                await asyncio.sleep(30)
                await msg.delete()

        except asyncio.TimeoutError:
            await ctx.send('Timeout!', delete_after=15)
            await asyncio.sleep(15)
            await ctx.message.delete()

    @staticmethod
    async def get_path(ctx, arg):
        valid = True
        all_channel = ctx.message.guild.voice_channels
        name_channel = [channel.name for channel in all_channel]
        if arg in [channel.name for channel in all_channel]:
            s_channel = all_channel[name_channel.index(arg)]
            path = config.path + "/" + str(ctx.message.guild.id) + "/" + str(s_channel.id)
        elif ctx.message.mentions:
            path = config.path + '/' + str(ctx.message.guild.id) + "/" + str(ctx.message.mentions[0].id)
        elif arg is None:
            path = config.path + "/" + str(ctx.message.guild.id)
        else:
            await ctx.send('No valid argument, please try again.'
                           '\nType "' + config.prefix + 'help" for more information')
            valid = False
            path = None

        return path, valid

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

        has_role = await self.required_role(ctx)
        if not has_role:
            return

        path, valid = await self.get_path(ctx, arg)

        if not valid:
            return

        songs = self.get_list_songs(path)

        if songs:

            list_songs = ""
            for index, song in enumerate(songs):
                list_songs = list_songs + str(index + 1) + ". " + song.split(".mp3")[0] + "\n"
            list_songs = list_songs + "**all**\n**cancel**"
            await ctx.send("List .mp3 files:\n" + list_songs, delete_after=30)

            await ctx.send("Choose a _number_ to delete a _**.mp3**_ file", delete_after=30)

            def check(m):
                return (m.content.isdigit() and m.author.guild.id == ctx.message.guild.id) \
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

        has_role = await self.required_role(ctx)
        if not has_role:
            return

        path, valid = await self.get_path(ctx, arg)

        if not valid:
            return

        songs = self.get_list_songs(path)

        if songs:

            list_songs = ""
            for index, song in enumerate(songs):
                list_songs = list_songs + str(index + 1) + ". " + song.split(".mp3")[0] + "\n"
            list_songs = list_songs + "**cancel**"
            await ctx.send("List .mp3 files:\n" + list_songs, delete_after=30)
            await ctx.send("Choose a _number_ to edit a _**.mp3**_ file _name_", delete_after=30)

            def check_number(m):
                return (m.content.isdigit() and m.author.guild.id == ctx.message.guild.id) \
                       or m.content == "cancel" or m.content == "Cancel" or m.content == "all" \
                       or m.content == "All"

            def check_name(m):
                return m.author.guild.id == ctx.message.guild.id \
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

    @staticmethod
    def dl_file(ctx, arg):
        all_channel = ctx.message.guild.voice_channels
        name_channel = [channel.name for channel in all_channel]
        if arg in [channel.name for channel in all_channel]:
            s_channel = all_channel[name_channel.index(arg)]
            file_path = 'audio/' + str(ctx.message.guild.id) + "/" + str(s_channel.id)
        elif arg is not None:
            file_path = 'audio/' + str(ctx.message.guild.id) + '/' + str(ctx.message.mentions[0].id)
        else:
            file_path = 'audio/' + str(ctx.message.guild.id)

        return file_path

    @commands.command(aliases=['Download', 'dl', 'Dl', 'DL'])
    async def download(self, ctx, arg=None):

        has_role = await self.required_role(ctx)
        if not has_role:
            return

        path, valid = await self.get_path(ctx, arg)

        if not valid:
            return

        songs = self.get_list_songs(path)

        if songs:

            list_songs = ""
            for index, song in enumerate(songs):
                list_songs = list_songs + str(index + 1) + ". " + song.split(".mp3")[0] + "\n"
            list_songs = list_songs + "**cancel**"
            await ctx.send("List .mp3 files:\n" + list_songs, delete_after=30)
            await ctx.send("Choose a _number_ to download a _**.mp3**_ file", delete_after=30)

            def check(m):
                return m.author.guild.id == ctx.message.guild.id \
                       or m.content == "cancel" or m.content == "Cancel"

            try:
                for i in range(3):

                    msg = await self.client.wait_for('message', check=check, timeout=30)
                    file_path = self.dl_file(ctx, arg)

                    if msg.content.isdigit() and int(msg.content) <= len(songs) and int(msg.content) != 0:
                        await ctx.send(file=discord.File(fp=file_path + '/' + songs[int(msg.content) - 1],
                                                         filename=songs[int(msg.content) - 1]))

                        await ctx.send('**' + songs[int(msg.content) - 1] + '** has been _**downloaded**_')
                        break

                    elif msg.content == "cancel" or msg.content == "Cancel":
                        await ctx.send("Nothing has been _**downloaded**_")
                        await msg.delete()
                        break
                    elif int(msg.content) > len(songs) or int(msg.content) == 0:
                        await ctx.send("That number is not an option. Try again **(" + str(i + 1) + "/3)**",
                                       delete_after=10)
                        if i == 2:
                            await ctx.send("None of the attempts were correct, _**download**_ has been aborted")
                    await msg.delete()
            except asyncio.TimeoutError:
                await ctx.send('Timeout!', delete_after=15)
                await asyncio.sleep(15)
                await ctx.message.delete()

    @commands.command(name='list', aliases=['show', 'List', 'Show'])
    async def show_list(self, ctx, arg=None):

        path, valid = await self.get_path(ctx, arg)

        if not valid:
            return

        songs = self.get_list_songs(path)

        if songs:
            list_songs = ""
            for index, song in enumerate(songs):
                list_songs = list_songs + str(index + 1) + ". " + song.split(".mp3")[0] + "\n"
            await ctx.send("List .mp3 files:\n" + list_songs, delete_after=60)
        else:
            await ctx.send('_List is empty_')

    @staticmethod
    async def path_zipping(ctx, arg):
        valid = True
        all_channel = ctx.message.guild.voice_channels
        name_channel = [channel.name for channel in all_channel]
        if arg in [channel.name for channel in all_channel]:
            s_channel = all_channel[name_channel.index(arg)]
            path = config.path + "/" + str(ctx.message.guild.id) + "/" + str(s_channel.id)
            filename = ctx.message.guild.name + "/" + s_channel.name
            file_path = str(ctx.message.guild.id) + "/" + str(s_channel.id)
        elif ctx.message.mentions:
            path = config.path + "/" + str(ctx.message.guild.id) + "/" + str(ctx.message.mentions[0].id)
            filename = ctx.message.guild.name + "/" + str(ctx.message.mentions[0])
            file_path = str(ctx.message.guild.id) + "/" + str(ctx.message.mentions[0].id)
        elif arg is None:
            path = config.path + "/" + str(ctx.message.guild.id)
            filename = ctx.message.guild.name
            file_path = str(ctx.message.guild.id)
        else:
            await ctx.send('No valid argument, please try again.'
                           '\nType "' + config.prefix + 'help" for more information')
            valid = False
            path = None
            filename = None
            file_path = None

        return path, filename, file_path, valid

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

        has_role = await self.required_role(ctx)

        if not has_role:
            return

        loop = self.client.loop or asyncio.get_event_loop()
        path, filename, file_path, valid = await self.path_zipping(ctx, arg)

        if not valid:
            return

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
