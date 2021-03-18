import asyncio
import functools
import logging
import os
import zipfile
from datetime import datetime
from os import listdir, stat
from os.path import isfile, join
from shutil import move

import discord
import mutagen
import requests
import youtube_dl
from discord.ext import commands
from pydub import AudioSegment

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

    @staticmethod
    def set_link_path(ctx, arg):
        all_channel = ctx.message.guild.voice_channels
        name_channel = [channel.name for channel in all_channel]
        if arg in [channel.name for channel in all_channel]:
            s_channel = all_channel[name_channel.index(arg)]
            link_path = 'audio/' + str(ctx.message.guild.id) + '/' + str(s_channel.id)
            absolute_path = config.path + '/' + str(ctx.message.guild.id) + '/' + str(s_channel.id)
            filename = ctx.message.guild.name + '/' + s_channel.name
        elif arg is not None:
            link_path = 'audio/' + str(ctx.message.guild.id) + '/' + str(ctx.message.mentions[0].id)
            absolute_path = config.path + '/' + str(ctx.message.guild.id) + '/' + str(ctx.message.mentions[0].id)
            filename = ctx.message.guild.name + '/' + ctx.message.mentions[0].name
        else:
            link_path = 'audio/' + str(ctx.message.guild.id)
            absolute_path = config.path + '/' + str(ctx.message.guild.id)
            filename = ctx.message.guild.name

        return link_path, absolute_path, filename

    @staticmethod
    async def link(ctx, url, path):

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:

                info_dict = ydl.extract_info(url, download=False)
                file_title = info_dict.get('id', None)
                file_duration = info_dict.get('duration', None)

            file_path = path + '/' + file_title + ".mp3"

            ydl_opts.update({'outtmpl': file_path})

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            return file_title, file_duration
        except Exception as e:
            logging.info(e)
            await ctx.send("The video is unavailable or that doesn't exist, **add** was aborted")
            return None, None

    @staticmethod
    async def delete_message(msg, time):
        await asyncio.sleep(time)
        await msg.delete()

    @staticmethod
    async def file_size(ctx, absolute_path, file_title):

        max_file_size = 8 * 1024 * 1024
        isvalid = True

        if max_file_size < stat(absolute_path + '/' + str(file_title) + '.mp3').st_size:
            await ctx.send("This size of the audio is too large, **add** was aborted")
            os.remove(absolute_path + '/' + str(file_title) + '.mp3')
            isvalid = False

        return isvalid

    @staticmethod
    async def choose_file_name(ctx, absolute_path, file_title, msg_name):

        name_valid = False

        if not os.path.exists(absolute_path + '/' + msg_name.content + '.mp3'):
            try:
                os.rename(absolute_path + '/' + str(file_title) + '.mp3',
                          absolute_path + '/' + msg_name.content + '.mp3')
            except Exception as e:
                logging.info(e)
                await ctx.send("Invalid name, please try a different name", delete_after=60)

            name_valid = True
        else:
            await ctx.send("This file already exists, please try a different name", delete_after=60)

        return name_valid

    @staticmethod
    async def valid_format(ctx, msg_time, file_duration):

        is_valid_format = True

        if str(msg_time.content).count(' to '):
            message = msg_time.content.split(' to ')
        else:
            is_valid_format = False
            await ctx.send("Incorrect format, please try again", delete_after=60)
            return 0, 0, 0, 0, is_valid_format

        begin = message[0].split(':')
        end = message[1].split(':')

        isvalid_begin = False
        isvalid_end = False
        begin0 = 0
        begin1 = 0
        end0 = 0
        end1 = 0

        if len(begin) == 1:
            isvalid_begin = begin[0].isdigit()
        elif len(begin) == 2:
            isvalid_begin = begin[0].isdigit() and begin[1].isdigit()

        if len(end) == 1:
            isvalid_end = end[0].isdigit()
        elif len(end) == 2:
            isvalid_end = end[0].isdigit() and end[1].isdigit()

        if isvalid_begin and isvalid_end:

            if len(begin) == 1:
                begin1 = int(begin[0])
            elif len(begin) == 2:
                begin0 = int(begin[0])
                begin1 = int(begin[1])

            if len(end) == 1:
                end1 = int(end[0])
            elif len(end) == 2:
                end0 = int(end[0])
                end1 = int(end[1])
        else:
            is_valid_format = False
            await ctx.send("Incorrect format, please try again", delete_after=60)
            return 0, 0, 0, 0, is_valid_format

        if begin0 * 60 + begin1 > file_duration or end0 * 60 + end1 > file_duration:
            await ctx.send("The audio segments should not surpass the file length, please try again", delete_after=60)
            is_valid_format = False
            return 0, 0, 0, 0, is_valid_format

        return begin0, begin1, end0, end1, is_valid_format

    @staticmethod
    async def confirm_file(ctx, absolute_path, msg_confirm, msg_name, filename):

        is_confirmed = False
        is_no = False

        if msg_confirm.content == "cancel" or msg_confirm.content == "Cancel":
            os.remove(absolute_path + '/' + msg_name.content + '.mp3')
            os.remove(absolute_path + '/' + msg_name.content + '_trim' + '.mp3')
            await ctx.send('Nothing has been _**added**_')

        elif msg_confirm.content == "yes" or msg_confirm.content == "Yes" or \
                msg_confirm.content == "YES" or msg_confirm.content == "y" or msg_confirm.content == "Y":
            os.remove(absolute_path + '/' + msg_name.content + '.mp3')
            os.rename(absolute_path + '/' + msg_name.content + '_trim' + '.mp3',
                      absolute_path + '/' + msg_name.content + '.mp3')
            await ctx.send('**' + msg_name.content + '.mp3' + '** was added to **' + filename + '**')
            is_confirmed = True
        elif msg_confirm.content == "no" or msg_confirm.content == "No" or msg_confirm.content == "NO" or \
                msg_confirm.content == "n" or msg_confirm.content == "N":
            os.remove(absolute_path + '/' + msg_name.content + '_trim' + '.mp3')
            await ctx.send('Please select the audio segment (**MM:SS** to **MM:SS**) you wish to use\n'
                           'This segment must not be longer than 10 seconds', delete_after=60)
            is_no = True

        return is_confirmed, is_no

    @staticmethod
    async def link_file(self, ctx, absolute_path, file_title, file_duration, link_path, filename, loop):

        isvalid = await self.file_size(ctx, absolute_path, file_title)
        if not isvalid:
            return

        while True:
            def check(m):
                return m.content == "cancel" or m.content == "Cancel" \
                       or (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id)

            await ctx.send("Choose a name for the new **.mp3** file", delete_after=60)
            msg_name = await self.client.wait_for('message', check=check, timeout=600)

            loop.create_task(self.delete_message(msg_name, 60))

            if msg_name.content == "cancel" or msg_name.content == "Cancel":
                await ctx.send('Nothing has been _**added**_')
                os.remove(absolute_path + '/' + str(file_title) + '.mp3')
                return

            name_valid = await self.choose_file_name(ctx, absolute_path, file_title, msg_name)

            if name_valid:
                break

        await ctx.send("File is uploading to trim... Please wait", delete_after=60)
        await ctx.send(file=discord.File(fp=link_path + '/' + msg_name.content + '.mp3',
                                         filename=msg_name.content + '.mp3'), delete_after=60)
        await ctx.send('Please select the audio segment (**MM:SS** to **MM:SS**) you wish to use\n'
                       'This segment must not be longer than 10 seconds', delete_after=60)

        while True:
            def check(m):
                return m.content == "cancel" or m.content == "Cancel" \
                       or (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id)

            msg_time = await self.client.wait_for('message', check=check, timeout=600)

            loop.create_task(self.delete_message(msg_time, 60))

            if msg_time.content == "cancel" or msg_time.content == "Cancel":
                await ctx.send('Nothing has been _**added**_')
                os.remove(absolute_path + '/' + msg_name.content + '.mp3')
                break

            begin0, begin1, end0, end1, is_valid_format = await self.valid_format(ctx, msg_time, file_duration)

            if not is_valid_format:
                continue

            if 0 <= end0 * 60 + end1 - (begin0 * 60 + begin1) <= 10:
                await ctx.send("File is trimming and uploading... Please wait", delete_after=60)
                file = AudioSegment.from_file(absolute_path + '/' + msg_name.content + '.mp3')
                file_trim = file[(begin0 * 60 + begin1) * 1000:(end0 * 60 + end1) * 1000]
                file_trim.export(absolute_path + '/' + msg_name.content + '_trim' + '.mp3', format="mp3")

                await ctx.send(file=discord.File(fp=link_path + '/' + msg_name.content + '_trim.mp3',
                                                 filename=msg_name.content + '_trim' + '.mp3'), delete_after=60)
                await ctx.send("Would you like to keep this **.mp3** file?\n"
                               "Type **yes** to keep it or **no** to cut it again, or **cancel**", delete_after=60)
                while True:
                    def check(m):
                        return m.content == "cancel" or m.content == "Cancel" or m.content == "yes" \
                               or m.content == "Yes" or m.content == "YES" or m.content == "y" or m.content == "Y" \
                               or m.content == "no" or m.content == "No" or m.content == "NO" or m.content == "n" \
                               or m.content == "N" and \
                               (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id)

                    msg_confirm = await self.client.wait_for('message', check=check, timeout=600)

                    loop.create_task(self.delete_message(msg_confirm, 60))

                    is_confirmed, is_no = await self.confirm_file(ctx, absolute_path, msg_confirm, msg_name, filename)

                    if is_confirmed or is_no:
                        break

                if is_confirmed:
                    break
                elif is_no:
                    continue

            else:
                await ctx.send("The file duration is longer than 10 seconds or lower than 0, please try again",
                               delete_after=60)

    @commands.command(aliases=['a', 'Add'])
    async def add(self, ctx, arg=None):

        has_role = await self.required_role(ctx)

        if not has_role:
            return

        loop = self.client.loop or asyncio.get_event_loop()
        valid = await self.create_folder(ctx, arg)

        if not valid:
            return

        await ctx.send("Upload a **.mp3** file, **youtube link** or **cancel**", delete_after=30)

        def check(m):
            return (m.content == "cancel" or m.content == "Cancel" or m.attachments or
                    'youtube' in m.content or 'youtu.be' in m.content) \
                   and (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id)

        try:
            msg = await self.client.wait_for('message', check=check, timeout=600)

            if msg.content == "cancel" or msg.content == "Cancel":
                await ctx.send('Nothing has been _**added**_')
                loop.create_task(self.delete_message(msg, 30))
                return

            if 'youtube' in msg.content or 'youtu.be' in msg.content:
                loop.create_task(self.delete_message(msg, 60))

                link_path, absolute_path, filename = self.set_link_path(ctx, arg)
                await ctx.send("Preparing file... Please wait", delete_after=60)
                file_title, file_duration = await self.link(ctx, msg.content, link_path)

                if file_title is None or file_duration is None:
                    return

                await self.link_file(self, ctx, absolute_path, file_title, file_duration, link_path, filename, loop)

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
            loop.create_task(self.delete_message(msg, 15))

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
                   and (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id)

        try:
            msg = await self.client.wait_for('message', check=check, timeout=30)

            if msg.content == "cancel" or msg.content == "Cancel":
                await ctx.send('Nothing has been _**unzipped**_')
                loop.create_task(self.delete_message(msg, 30))
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
                loop.create_task(self.delete_message(msg, 30))
            else:
                os.remove('audio/' + file_path + '.zip')
                await ctx.send(msg.attachments[0].filename + ' was not a valid _**.zip**_ file')
                loop.create_task(self.delete_message(msg, 30))

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

        loop = self.client.loop or asyncio.get_event_loop()

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
                return (m.content.isdigit() and
                        m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
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
                        loop.create_task(self.delete_message(msg, 30))
                        break
                    elif msg.content == "all" or msg.content == "All":
                        for index in range(len(songs)):
                            os.remove(path + '/' + songs[index])
                        await ctx.send('All the _**.mp3**_ files has been _**deleted**_')
                        loop.create_task(self.delete_message(msg, 30))
                        break
                    elif int(msg.content) > len(songs) or int(msg.content) == 0:
                        await ctx.send("That number is not an option. Try again **(" + str(i + 1) + "/3)**",
                                       delete_after=10)
                        if i == 2:
                            await ctx.send("None of the attempts were correct, _**delete**_ has been aborted")
                    loop.create_task(self.delete_message(msg, 10))

            except asyncio.TimeoutError:
                await ctx.send('Timeout!', delete_after=15)
                await asyncio.sleep(15)
                await ctx.message.delete()
        else:
            await ctx.send('_List is empty_')

    @commands.command(aliases=['Edit'])
    async def edit(self, ctx, arg=None):

        loop = self.client.loop or asyncio.get_event_loop()

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
                return (m.content.isdigit() and
                        m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                       or m.content == "cancel" or m.content == "Cancel" or m.content == "all" \
                       or m.content == "All"

            def check_name(m):
                return (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                       or m.content == "cancel" or m.content == "Cancel"

            try:
                for i in range(3):

                    msg = await self.client.wait_for('message', check=check_number, timeout=30)

                    if msg.content.isdigit() and int(msg.content) <= len(songs) and int(msg.content) != 0:

                        await ctx.send("Choose a new _name_ or type _**cancel**_ to not edit", delete_after=30)
                        msg_edit = await self.client.wait_for('message', check=check_name, timeout=60)

                        if msg_edit.content == 'cancel' or msg_edit.content == 'Cancel':
                            await ctx.send("Nothing has been _**edited**_")
                        else:
                            os.rename(path + '/' + songs[int(msg.content) - 1],
                                      path + '/' + msg_edit.content + '.mp3')
                            await ctx.send('**' + songs[int(msg.content) - 1] +
                                           '** has been edited to **' + msg_edit.content + '.mp3**')
                        loop.create_task(self.delete_message(msg, 30))
                        loop.create_task(self.delete_message(msg_edit, 30))
                        break
                    elif msg.content == "cancel" or msg.content == "Cancel":
                        await ctx.send("Nothing has been _**edited**_")
                        loop.create_task(self.delete_message(msg, 30))
                        break
                    elif int(msg.content) > len(songs) or int(msg.content) == 0:
                        await ctx.send("That number is not an option. Try again **(" + str(i + 1) + "/3)**",
                                       delete_after=10)
                        if i == 2:
                            await ctx.send("None of the attempts were correct, _**edit**_ has been aborted")
                    loop.create_task(self.delete_message(msg, 30))
            except asyncio.TimeoutError:
                await ctx.send('Timeout!', delete_after=15)
                await asyncio.sleep(15)
                await ctx.message.delete()
        else:
            await ctx.send('_List is empty_')

    @staticmethod
    def path_file(ctx, arg):
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

        loop = self.client.loop or asyncio.get_event_loop()

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
                return (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                       or m.content == "cancel" or m.content == "Cancel"

            try:
                for i in range(3):

                    msg = await self.client.wait_for('message', check=check, timeout=30)
                    file_path = self.path_file(ctx, arg)

                    if msg.content.isdigit() and int(msg.content) <= len(songs) and int(msg.content) != 0:
                        await ctx.send(file=discord.File(fp=file_path + '/' + songs[int(msg.content) - 1],
                                                         filename=songs[int(msg.content) - 1]))

                        await ctx.send('**' + songs[int(msg.content) - 1] + '** has been _**downloaded**_')
                        loop.create_task(self.delete_message(msg, 10))
                        break

                    elif msg.content == "cancel" or msg.content == "Cancel":
                        await ctx.send("Nothing has been _**downloaded**_")
                        loop.create_task(self.delete_message(msg, 10))
                        break
                    elif int(msg.content) > len(songs) or int(msg.content) == 0:
                        await ctx.send("That number is not an option. Try again **(" + str(i + 1) + "/3)**",
                                       delete_after=10)
                        if i == 2:
                            await ctx.send("None of the attempts were correct, _**download**_ has been aborted")
                    loop.create_task(self.delete_message(msg, 10))
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

    @commands.command()
    async def change_volume(self, ctx, path, songs, msg_number, loop, file_path):

        def check_volume(m):
            return (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                   or m.content == "cancel" or m.content == "Cancel"

        song = AudioSegment.from_file(path + '/' + songs[int(msg_number.content) - 1])

        percent_current = (float(song.dBFS) + 66)
        await ctx.send("This is the current volume: " + str(int(percent_current)))
        await ctx.send("Choose a number **(0-50)** or **cancel**")

        while True:
            msg_volume = await self.client.wait_for('message', check=check_volume, timeout=60)

            if msg_volume.content == "cancel" or msg_volume.content == "Cancel":
                await ctx.send("_**Volume**_ has not been changed")
                loop.create_task(self.delete_message(msg_volume, 10))
                loop.create_task(self.delete_message(msg_number, 10))
                return

            is_valid = True

            if msg_volume.content.count('-') == 1:
                number = msg_volume.content.split('-')[1]
            elif msg_volume.content.count('-') > 1:
                number = 0
                is_valid = False
            else:
                number = msg_volume.content

            if is_valid and number.isdigit():

                percent = float(msg_volume.content)
                percent = 50 - percent
                percent = percent + 15 + float(song.dBFS)

                if float(0) <= float(msg_volume.content) <= float(50):

                    song = song - float(percent)
                    song.export(file_path + '/' + songs[int(msg_number.content) - 1], format='mp3')

                    await ctx.send('**' + songs[int(msg_number.content) - 1] +
                                   '** has been changed to **' + str(msg_volume.content) + '**')
                    break
                else:
                    loop.create_task(self.delete_message(msg_volume, 30))
                    await ctx.send("That **volume** is not valid, try again", delete_after=30)
                    continue
            else:
                loop.create_task(self.delete_message(msg_volume, 30))
                await ctx.send("That is not a number, try again", delete_after=30)
                continue

    @commands.command(aliases=['vol', 'Volume', 'Vol'])
    async def volume(self, ctx, arg=None):

        loop = self.client.loop or asyncio.get_event_loop()

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
                return (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                       or m.content == "cancel" or m.content == "Cancel"

            try:

                for i in range(3):
                    file_path = self.path_file(ctx, arg)
                    msg_number = await self.client.wait_for('message', check=check_number, timeout=60)
                    if msg_number.content.isdigit() and int(msg_number.content) <= len(songs) \
                            and int(msg_number.content) != 0:

                        await self.change_volume(ctx, path, songs, msg_number, loop, file_path)
                        break

                    elif msg_number.content == "cancel" or msg_number.content == "Cancel":
                        await ctx.send("_**Volume**_ has not been changed")
                        loop.create_task(self.delete_message(msg_number, 10))
                        break
                    elif msg_number.content.isdigit() and \
                            (int(msg_number.content) > len(songs) or int(msg_number.content) == 0):
                        await ctx.send("That number is not an option. Try again **(" + str(i + 1) + "/3)**",
                                       delete_after=10)
                        if i == 2:
                            await ctx.send("None of the attempts were correct, _**download**_ has been aborted")
                    else:
                        await ctx.send("That is not a number, try again")
                    loop.create_task(self.delete_message(msg_number, 10))
            except asyncio.TimeoutError:
                await ctx.send('Timeout!', delete_after=15)
                await asyncio.sleep(15)
                await ctx.message.delete()
        else:
            await ctx.send('_List is empty_')


def setup(client):
    client.add_cog(FileManagement(client))
