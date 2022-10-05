import asyncio
import datetime
import functools
import logging
import os
import zipfile
from datetime import datetime
from os import stat

import discord
import mutagen
import requests
from discord.ext import commands

import config


class FileManagement(commands.Cog):

    def __init__(self, client):
        self.client = client

    @staticmethod
    async def valid_folder(self, ctx, arg):
        path = f"{config.path}/{ctx.message.guild.id}"
        valid = True
        if ctx.message.mentions or arg is None:
            new_path = path
        else:
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 'No valid argument, please try again.\n'
                                 f"\nType ** {config.prefix}help** for more information", 30)
            valid = False
            new_path = None

        if valid and not os.path.exists(new_path):
            os.makedirs(new_path)

        return path, valid

    @staticmethod
    async def file_size(self, ctx, file_title):

        max_file_size = 8 * 1024 * 1024
        isvalid = True

        path = f"{config.path}/{ctx.message.guild.id}"

        file_path = f"{path}/{file_title}.mp3"

        if max_file_size < stat(path).st_size:
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 "This size of the audio is too large, **wavU** could not add it", 30)
            os.remove(file_path)
            isvalid = False

        return isvalid

    @staticmethod
    async def choose_file_name(self, ctx, file_title, msg_name):

        name_valid = False

        if not os.path.exists(f"{config.path}/{msg_name.content}.mp3"):
            try:
                os.rename(f"{config.path}/{str(file_title)}.mp3",
                          f"{config.path}/{msg_name.content}.mp3")
            except Exception as e:
                logging.info(e)
                await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                     "Invalid name, please try a different name", 60)
            name_valid = True
        else:
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 "This file already exists, please try a different name", 60)
        return name_valid

    @staticmethod
    def time_parser(times):
        time = 0

        if len(times) == 1:
            return times[0]

        for index, t in enumerate(times):
            if index == 0:
                time += t * 60
            elif index == 1:
                time += t
            else:
                time += t / 1000

        return time

    @staticmethod
    async def valid_format(self, ctx, msg_time, file_duration):

        is_valid_format = False
        begin_times = 0
        end_times = 0

        if str(msg_time.content).count(' to '):
            message = msg_time.content.split(' to ')
        elif str(msg_time.content).lower() == "entire":
            if 10 > file_duration:
                return 0, file_duration, True
            else:
                await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                     "The entire video is longer than 10 seconds, please try again", 60)
                return begin_times, end_times, is_valid_format
        else:
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 "Incorrect format, please try again", 60)
            return begin_times, end_times, is_valid_format

        begin = message[0].split(':')
        end = message[1].split(':')

        isvalid_begin = sum(map(lambda x: x.isdigit(), begin))
        isvalid_end = sum(map(lambda x: x.isdigit(), end))

        if isvalid_begin and isvalid_end:

            list_times_begin = list(map(lambda x: int(x), begin))
            list_times_end = list(map(lambda x: int(x), end))

            begin_times = self.time_parser(list_times_begin)
            end_times = self.time_parser(list_times_end)

        else:
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 "Incorrect format, please try again", 60)
            return begin_times, end_times, is_valid_format

        if begin_times > file_duration or end_times > file_duration:
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 "The audio segments should not surpass the file length, please try again", 60)
            return begin_times, end_times, is_valid_format

        return begin_times, end_times, True

    @staticmethod
    async def confirm_file(self, ctx, arg, msg_confirm, msg_name):

        is_confirmed = False
        is_no = False

        if str(msg_confirm.content).lower() == "cancel":
            os.remove(f"{config.path}/{msg_name.content}.mp3")
            os.remove(f"{config.path}/{msg_name.content}_trim.mp3")
            await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                 "Nothing has been **added**", 30)

        elif str(msg_confirm.content).lower() in "yes":
            os.remove(f"{config.path}/{msg_name.content}.mp3")
            os.rename(f"{config.path}/{msg_name.content}_trim.mp3",
                      f"{config.path}/{msg_name.content}.mp3")
            await self.insert_file_db(self, ctx, arg, f"{msg_name.content}.mp3")
            is_confirmed = True
        elif str(msg_confirm.content).lower() in "no":
            os.remove(f"{config.path}/{msg_name.content}_trim.mp3")
            await self.embed_msg(ctx, f"Let's try again {ctx.message.author.name}",
                                 "I need the audio segment to cut your audio\n"
                                 "Format: (**MM:SS:MS** to **MM:SS:MS**)\n"
                                 "MM = Minutes, SS = Seconds, MS = Milliseconds.\n"
                                 "If you want the entire audio type *entire*\n"
                                 "This segment must not be longer than 10 seconds.", 60)
            is_no = True

        return is_confirmed, is_no

    @staticmethod
    def unzip_songs(self, ctx, path, r, zip_name):

        with open(f"audio/{zip_name}", 'wb') as f:
            for chunk in r.iter_content():
                if chunk:
                    f.write(chunk)
        f.close()

        with zipfile.ZipFile(f"audio/{zip_name}", 'r') as zip_ref:
            files = zip_ref.namelist()
            valid_files = []
            invalid_files_format = []
            already_exist = []
            for file in files:
                mp3 = file.split('.')
                if mp3[len(mp3) - 1] != "mp3":
                    invalid_files_format.append(file)
                else:
                    file_exists = self.files_collection.find_one({"guild_id": ctx.message.guild.id,
                                                                  "audio_name": file})
                    if file_exists:
                        already_exist.append(file)
                    else:
                        valid_files.append(file)

            invalid_files_duration = []

            if valid_files:
                zip_ref.extractall(path, members=valid_files)
                zip_ref.close()

                for file in valid_files:
                    filepath = f"{path}/{file}"
                    audio = mutagen.File(filepath)
                    d = datetime.fromtimestamp(int(audio.info.length)).strftime("%M:%S")
                    if int(audio.info.length) >= 10:
                        invalid_files_duration.append((file, d))
                        os.remove(filepath)

                for file in invalid_files_duration:
                    valid_files.remove(file[0])

        return valid_files, invalid_files_format, invalid_files_duration, already_exist

    @commands.command(aliases=['Unzip'])
    async def unzip(self, ctx, arg=None):

        has_role = await self.required_role(self, ctx)

        if not has_role:
            return

        loop = self.client.loop or asyncio.get_event_loop()

        path, valid = await self.valid_folder(self, ctx, arg)

        if not valid:
            return

        await self.embed_msg(ctx, f"Hi {ctx.message.author.name}! Glad to see you :heart_eyes:",
                             f"Upload a **.zip** file or **cancel**", 30)

        def check(m):
            return (str(m.content).lower() == "cancel" or m.attachments) \
                   and (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id)

        try:
            msg = await self.client.wait_for('message', check=check, timeout=30)

            if str(msg.content).lower() == "cancel":
                await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                     "Nothing has been _**unzipped**_")
                loop.create_task(self.delete_message(msg, 30))
                return

            headers = {
                'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
            }

            r = requests.get(msg.attachments[0].url, headers=headers, stream=False)
            zip_name = msg.attachments[0].filename

            async with ctx.typing():
                fn = functools.partial(self.unzip_songs, self, ctx, path, r, zip_name)
                valid_files, invalid_files_format, invalid_files_duration, already_exist = \
                    await loop.run_in_executor(None, fn)

            if valid_files:
                os.remove(f"audio/{zip_name}")

                valid_text = ""
                if valid_files:
                    valid_text = "Valid files:\n"
                    for file in valid_files:
                        valid_text = f"{valid_text} :white_check_mark: {file}\n"
                        await self.insert_file_db(self, ctx, arg, file)

                already_exist_text = ""
                if already_exist:
                    already_exist_text = "Files already exist:\n"

                    for file in already_exist:
                        already_exist_text = f"{already_exist_text} :x: {file}\n"

                invalid_format_text = ""
                if invalid_files_format:
                    invalid_format_text = "Invalid files format:\n"

                    for file in invalid_files_format:
                        invalid_format_text = f"{invalid_format_text} :x: {file}\n"

                invalid_duration_text = ""
                if invalid_files_duration:
                    invalid_duration_text = "Invalid files duration:\n"

                    for file in invalid_files_duration:
                        invalid_duration_text = f"{invalid_duration_text} :x: {file[0]} {file[1]}\n"

                await self.embed_msg(ctx, f"{msg.attachments[0].filename} was added to {ctx.message.guild.name}",
                                     f"{valid_text} {invalid_format_text} {invalid_duration_text} {already_exist_text}")
                loop.create_task(self.delete_message(msg, 30))
            else:
                os.remove(f"audio/{zip_name}")
                await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                     f"{msg.attachments[0].filename} was not a valid **.zip** file'")
                loop.create_task(self.delete_message(msg, 30))

        except asyncio.TimeoutError:
            await ctx.send('Timeout!', delete_after=15)
            await asyncio.sleep(15)
            await ctx.message.delete()

    @staticmethod
    def get_list_songs(self, ctx, arg):

        guild_id = ctx.message.guild.id
        user_id = int(arg[2:-1]) if arg is not None else 0

        if arg is None:
            audios = self.files_collection.find({"guild_id": guild_id, "user_id": 0})
        else:
            audios = self.files_collection.find({"guild_id": guild_id, "user_id": user_id})
        audios = list(audios)

        songs = list(map(lambda audio: audio["audio_name"], audios))

        return songs

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

                        if str(msg_edit.content).lower() == "cancel":
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
                       or str(m.content).lower() == "cancel"

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

        songs = self.get_list_songs(self, ctx, arg)

        if songs:
            list_songs = ""
            for index, song in enumerate(songs):
                list_songs = list_songs + str(index + 1) + ". " + song.split(".mp3")[0] + "\n"
            await self.embed_msg(ctx, f"List .mp3 files:",
                                 list_songs, 60)
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                 "List is empty", 30)

    @staticmethod
    def zipping(self, ctx, arg, filename, path):
        file_zip = zipfile.ZipFile(f"audio/{filename}.zip", 'w', zipfile.ZIP_DEFLATED)
        is_empty = False

        songs = self.get_list_songs(self, ctx, arg)

        if not songs:
            is_empty = True
            return is_empty

        for root, dirs, files in os.walk(path):
            for file in files:
                if file in songs:
                    song = file.split('.')
                    if song[len(song) - 1] == "mp3":
                        file_zip.write(os.path.join(root, file),
                                       os.path.relpath(os.path.join(root + '/' + filename, file),
                                                       os.path.join(path, filename)))

        file_zip.close()

        return is_empty

    @commands.command(aliases=['Zip', 'z', 'Z'])
    async def zip(self, ctx, arg=None):

        has_role = await self.required_role(self, ctx)

        if not has_role:
            return

        loop = self.client.loop or asyncio.get_event_loop()

        path, valid = await self.valid_folder(self, ctx, arg)

        if not valid:
            return

        guild_name = ctx.message.guild.name

        if arg is None:
            filename = guild_name
        else:
            filename = f"{guild_name}/{ctx.message.author.name}"

        async with ctx.typing():
            fn = functools.partial(self.zipping, self, ctx, arg, guild_name, path)
            is_empty = await loop.run_in_executor(None, fn)

        if not is_empty:
            await ctx.send(file=discord.File(fp=f"audio/{guild_name}.zip", filename=f"{filename}.zip"))
            os.remove(f"{config.path}/{guild_name}.zip")
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                 "There's no file to add to **zip**")

    @commands.command()
    async def change_volume(self, ctx, path, songs, msg_number, loop, file_path):

        def check_volume(m):
            return (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                   or str(m.content).lower() == "cancel"

        song = AudioSegment.from_file(path + '/' + songs[int(msg_number.content) - 1])

        percent_current = (float(song.dBFS) + 66)
        await self.embed_msg(ctx, f"This is the current volume: {int(percent_current)}",
                             "Choose a number **(0-50)** or **cancel**")

        while True:
            msg_volume = await self.client.wait_for('message', check=check_volume, timeout=60)

            if str(msg_volume.content).lower() == "cancel":
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
                await self.embed_msg(ctx, f"Timeout!",
                                     'This command was cancelled', 15)
                await asyncio.sleep(15)
                await ctx.message.delete()
        else:
            await ctx.send('_List is empty_')


'''
@staticmethod
    async def embed_list(self, ctx):

        dirnames_aux = []
        list_tab = []
        title_tab = ""
        file_tab = ""
        user_index = 0
        file_tabs = []
        filenames_list = []

        # Go through directories and get the user/channel id and base case get all the common files
        for (dirpath, dirnames, filenames) in walk(config.path + "/" + str(ctx.message.guild.id)):
            if dirnames:
                title_tab = "**Common:**\n"
                dirnames_aux = dirnames.copy()
            else:
                try:
                    user = await self.client.fetch_user(dirnames_aux[user_index])
                except:
                    user = None
                try:
                    channel = await self.client.fetch_channel(dirnames_aux[user_index])
                except:
                    channel = None

                if user:
                    title_tab = "**Member: " + user.name + "**\n"
                elif channel:
                    title_tab = "**Channel: " + channel.name + "**\n"

                user_index += 1

            filenames_list.append([filenames[i:i + 10] for i in range(0, len(filenames), 10)])

            # Enlist 10 first files on common files
            for index, filename in enumerate(filenames):
                if (index + 1) % 10 == 0:
                    file_tab = file_tab + str(10) + '. ' + filename + '\n'
                    file_tabs.append(file_tab)
                    file_tab = ""
                else:
                    file_tab = file_tab + str((index + 1) % 10) + '. ' + filename + '\n'
            if file_tab != "":
                file_tabs.append(file_tab)

            if file_tabs:
                list_tab.append([title_tab, file_tabs])
            file_tabs = []
            file_tab = ""

        return list_tab, filenames_list, dirnames_aux

    @staticmethod
    async def core_reactions(msg_em, filenames, dict_numbers):
        await msg_em.add_reaction('⬅️')
        await msg_em.add_reaction('❌')
        await msg_em.add_reaction('➡️')

        for ind in range(len(filenames[0][0])):
            await msg_em.add_reaction(dict_numbers[str(ind + 1)])
            await asyncio.sleep(0.1)

    @staticmethod
    async def change_page(index, jndex, reaction, embed, prev_pages_len, list_tab, msg_em, current_pages_len,
                          last_pages_len, first_pages_len):

        # index == Tab && jndex == Page
        # list_tab[tab][page]

        # Go left when tab is not on the first one
        if str(reaction.emoji) == "⬅️" and index > 0:
            embed.clear_fields()
            # Tab > 0 and Before Tab == 0 and Current page == 0
            if prev_pages_len == 0 and jndex == 0:
                print("left1")
                embed.add_field(
                    name=list_tab[index - 1][0] + str(prev_pages_len + 1) + '/' + str(prev_pages_len + 1),
                    value=list_tab[index - 1][1][0])
                index -= 1
                jndex = prev_pages_len
            # Tab > 0 and Before Tab > 0 and Current page == 0
            elif prev_pages_len > 0 and jndex == 0:
                print("left2")
                embed.add_field(
                    name=list_tab[index - 1][0] + str(prev_pages_len + 1) + '/' + str(prev_pages_len + 1),
                    value=list_tab[index - 1][1][prev_pages_len])
                index -= 1
                jndex = prev_pages_len
            # Tab > 0 and current page < 0
            elif jndex > 0:
                print("left3")
                embed.add_field(name=list_tab[index][0] + str(jndex) + '/' + str(current_pages_len),
                                value=list_tab[index][1][jndex - 1])
                jndex -= 1

            await msg_em.edit(embed=embed)
        # Go right when tab is not on the last one
        elif str(reaction.emoji) == "➡️" and index < len(list_tab) - 1:
            embed.clear_fields()
            # len(pages) == 0
            if len(list_tab[index][1]) - 1 == 0:
                print("right1")
                embed.add_field(name=list_tab[index + 1][0] + str(1) + '/' + str(len(list_tab[index + 1][1])),
                                value=list_tab[index + 1][1][0])
                jndex = 0
                index += 1
            # 0 < len(pages) < page(current)
            elif len(list_tab[index][1]) - 1 > 0 and len(list_tab[index][1]) - 1 > jndex:
                print("right2")
                embed.add_field(name=list_tab[index][0] + str(jndex + 2) + '/' + str(current_pages_len),
                                value=list_tab[index][1][jndex + 1])
                jndex += 1
            # 0 < len(pages) and len(pages) == page(current)
            elif 0 < len(list_tab[index][1]) - 1 == jndex:
                print("right3")
                embed.add_field(name=list_tab[index + 1][0] + str(1) + '/' + str(len(list_tab[index + 1][1])),
                                value=list_tab[index + 1][1][0])
                jndex = 0
                index += 1

            await msg_em.edit(embed=embed)
        # Go left when tab is on the first one
        elif str(reaction.emoji) == "⬅️" and index == 0:
            embed.clear_fields()
            # Tab == 0 and Before Tab == 0 and Current page == 0
            if jndex == 0:
                print("left4")
                embed.add_field(name=(list_tab[len(list_tab) - 1][0] + str(last_pages_len + 1) +
                                      '/' + str(last_pages_len + 1)),
                                value=list_tab[len(list_tab) - 1][1][last_pages_len])
                jndex = last_pages_len
                index = len(list_tab) - 1
            # Tab == 0 and page > 0
            elif jndex > 0:
                print("left5")
                embed.add_field(name=list_tab[index][0] + str(jndex) + '/' + str(current_pages_len),
                                value=list_tab[index][1][jndex - 1])
                jndex -= 1
            await msg_em.edit(embed=embed)
        elif str(reaction.emoji) == "➡️" and index == len(list_tab) - 1:
            embed.clear_fields()
            if len(list_tab[index][1]) - 1 == jndex:
                print("right4")
                embed.add_field(name=list_tab[0][0] + str(1) + '/' + str(first_pages_len + 1),
                                value=list_tab[0][1][0])
                index = 0
                jndex = 0
            elif len(list_tab[index][1]) - 1 > jndex:
                print("right5")
                embed.add_field(name=list_tab[index][0] + str(jndex + 2) + '/' + str(current_pages_len),
                                value=list_tab[index][1][jndex + 1])
                jndex += 1
            await msg_em.edit(embed=embed)

        return index, jndex

    @staticmethod
    async def arrows(self, ctx, list_tab, dict_numbers, filenames, dirnames, voice):

        def check(reaction, user):
            return user != self.client.user and user.guild.id == ctx.guild.id

        loop = self.client.loop or asyncio.get_event_loop()

        index = 0
        jndex = 0
        embed = discord.Embed(title='Choose a file to play', color=0xFC65E1)
        embed.add_field(name=list_tab[index][0] + str(jndex + 1) + '/' + str(len(list_tab[index][1])),
                        value=list_tab[index][1][0])
        msg_em = await ctx.send(embed=embed)

        task_core_reaction = loop.create_task(self.core_reactions(msg_em, filenames, dict_numbers))

        task_arrows = None

        while True:
            reaction, user = await self.client.wait_for('reaction_add', check=check)

            prev_pages_len = len(list_tab[index - 1][1]) - 1
            last_pages_len = len(list_tab[len(list_tab) - 1]) - 1
            current_pages_len = len(list_tab[index][1])
            first_pages_len = len(list_tab[0][1]) - 1

            index, jndex = await self.change_page(index, jndex, reaction, embed, prev_pages_len, list_tab, msg_em,
                                                  current_pages_len, last_pages_len, first_pages_len)

            if reaction:
                await asyncio.sleep(0.1)
                await msg_em.remove_reaction(emoji=reaction.emoji, member=user)

            if str(reaction.emoji) == "➡️" or str(reaction.emoji) == "⬅️":
                if task_arrows is not None:
                    await task_arrows
                if task_core_reaction is not None:
                    await task_core_reaction

                task_arrows = loop.create_task(self.arrows_reactions(index, jndex, filenames,
                                                                     task_arrows, msg_em, self.client.user,
                                                                     dict_numbers))

            if str(reaction.emoji) == '1️⃣' or str(reaction.emoji) == '2️⃣' or str(reaction.emoji) == '3️⃣' or \
                    str(reaction.emoji) == '4️⃣' or str(reaction.emoji) == '5️⃣' or str(reaction.emoji) == '6️⃣' or \
                    str(reaction.emoji) == '7️⃣' or str(reaction.emoji) == '8️⃣' or str(reaction.emoji) == '9️⃣' or \
                    str(reaction.emoji) == '🔟':
                await self.chosen_file(self, ctx, reaction, filenames, dirnames, index, jndex, dict_numbers)

            if str(reaction.emoji) == '❌':
                db.sound_pad_state(0, str(ctx.guild.id))
                await msg_em.delete()
                embed = discord.Embed(title='Soundpad is off', color=0xFC65E1)
                await ctx.send(embed=embed)
                await voice.disconnect()
                return

    @staticmethod
    async def arrows_reactions(index, jndex, filenames, prev_num_len, msg_em, user, dict_numbers):

        actual_num_len = filenames[index][jndex]

        if prev_num_len is None:
            prev_num_len = filenames[0][0]
        else:
            prev_num_len = prev_num_len.result()

        if len(actual_num_len) < len(prev_num_len):
            remove = len(prev_num_len) - len(actual_num_len)
            for ind in range(remove):
                await asyncio.sleep(0.1)
                await msg_em.remove_reaction(emoji=dict_numbers[str(len(prev_num_len) - ind)], member=user)
        else:
            add = len(actual_num_len) - len(prev_num_len)
            for ind in range(add):
                await asyncio.sleep(0.1)
                await msg_em.add_reaction(dict_numbers[str(len(prev_num_len) + ind + 1)])

        return actual_num_len

    @staticmethod
    async def chosen_file(self, ctx, reaction, filenames, dirnames, index, jndex, dict_numbers):
        loop = self.client.loop or asyncio.get_event_loop()
        if ctx.author.voice is None:
            await ctx.send("You need to be connected on a **Voice channel**")
            return

        songs = filenames[index][jndex]

        try:
            if index == 0:
                path_to_play = 'audio/' + str(ctx.message.guild.id) + '/' + \
                               str(songs[int(dict_numbers[str(reaction.emoji)]) - 1])
            else:
                path_to_play = 'audio/' + str(ctx.message.guild.id) + '/' + dirnames[index - 1] + '/' + \
                               str(songs[int(dict_numbers[str(reaction.emoji)]) - 1])

            voice = get(self.client.voice_clients, guild=ctx.author.guild)
            if str(ctx.guild.id) not in self.queue:
                await self.start_playing(self, ctx, voice, path_to_play)
            else:
                self.queue[str(ctx.guild.id)].append(path_to_play)
        except Exception as e:
            print(str(e))
            pass

    @staticmethod
    async def start_playing(self, ctx, voice, path_to_play):
        loop = self.client.loop or asyncio.get_event_loop()
        self.queue[str(ctx.guild.id)] = [path_to_play]

        i = 0
        while i < len(self.queue[str(ctx.guild.id)]):
            partial = functools.partial(voice.play, discord.FFmpegPCMAudio(self.queue[str(ctx.guild.id)][i]))
            await loop.run_in_executor(None, partial)
            while voice.is_playing():
                await asyncio.sleep(0.3)
            i += 1

        del self.queue[str(ctx.guild.id)]

    @commands.command(aliases=['sp', 'Soundpad', 'Sp', 'SP', 'SoundPad'])
    async def soundpad(self, ctx):

        has_role = await self.required_role(ctx)
        if not has_role:
            return

        if ctx.author.voice is None:
            await ctx.send("You need to be connected on a **Voice channel**")
            return

        db.sound_pad_state(1, str(ctx.guild.id))

        channel = ctx.author.voice.channel
        voice = await channel.connect()

        list_tab, filenames, dirnames = await self.embed_list(self, ctx)

        dict_numbers = {'1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣', '5': '5️⃣',
                        '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣', '10': '🔟',
                        '1️⃣': '1', '2️⃣': '2', '3️⃣': '3', '4️⃣': '4', '5️⃣': '5',
                        '6️⃣': '6', '7️⃣': '7', '8️⃣': '8', '9️⃣': '9', '🔟': '10'}

        await self.arrows(self, ctx, list_tab, dict_numbers, filenames, dirnames, voice)
'''


def setup(client):
    client.add_cog(FileManagement(client))
