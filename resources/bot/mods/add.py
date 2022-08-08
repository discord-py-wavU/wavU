import functools
import os
from discord.ext import commands
import asyncio
import hashlib
import mutagen
import requests
from resources.bot.helpers import Helpers
import config
import logging
import youtube_dl
import discord
from pydub import AudioSegment


class AddCommand(commands.Cog, Helpers):

    def __init__(self, client):
        self.client = client

    @staticmethod
    async def get_file_info(self, ctx, url):

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

            file_path = f"{config.path}/{file_title}.mp3"

            ydl_opts.update({'outtmpl': file_path})

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            return file_title, file_duration
        except Exception as e:
            logging.info(e)
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 "The video was unavailable or does not exist, **wavU** could not add it", 30)
            return None, None

    @staticmethod
    async def link_file(self, ctx, arg, file_title, file_duration, loop):

        isvalid = await self.file_size(self, ctx, file_title)
        if not isvalid:
            return

        await self.embed_msg(ctx, f"Please {ctx.message.author.name}",
                             "Choose a name for the new file", 60)

        while True:
            def check(m):
                return str(m.content).lower() == "cancel" \
                       or (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id)

            # Waiting for file name
            msg_name = await self.client.wait_for('message', check=check, timeout=600)

            # Check if name exists on this guild
            q = {"_id": ctx.message.guild.id, "audios.name": {"$in": msg_name.content}}
            file_server_exists = self.servers_collection.find_one(q)

            # Check if name exists on some member or channel of this guild
            q = {"_id": f"{ctx.message.guild.id}/{ctx.message.author.id}",
                 "audios.name": {"$in": msg_name.content}}
            file_member_exists = self.entities_collection.find_one(q)

            hashcode = hashlib.md5(open(f"{config.path}/{msg_name.content}.mp3", 'rb').read()).hexdigest()

            if file_server_exists or file_member_exists:
                await ctx.send(file=discord.File(fp=f"{config.path}/{msg_name.content}.mp3",
                                                 filename=f"{msg_name.content}.mp3"), delete_after=60)
                await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                     "This name already exists, try again",
                                     60)
                continue
            # elif os.path.exists(f"{hashcode}.mp3"):

            loop.create_task(self.delete_message(msg_name, 60))

            if str(msg_name.content).lower() == "cancel":
                await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                     "Nothing has been **added**", 30)
                os.remove(f"{config.path}/{file_title}.mp3")
                return

            name_valid = await self.choose_file_name(self, ctx, file_title, msg_name)

            if name_valid:
                break

        await self.embed_msg(ctx, f"I'm working on your file",
                             "Please wait a few seconds", 60)
        await ctx.send(file=discord.File(fp=f"{config.path}/{msg_name.content}.mp3",
                                         filename=f"{msg_name.content}.mp3"), delete_after=60)
        await self.embed_msg(ctx, f"Let's do this {ctx.message.author.name}",
                             "I need the audio segment to cut your audio\n"
                             "Format: (**MM:SS:MS** to **MM:SS:MS**)\n"
                             "MM = Minutes, SS = Seconds, MS = Milliseconds.\n"
                             "If you want the entire audio type *entire*\n"
                             "This segment must not be longer than 10 seconds.", 60)

        while True:
            def check(m):
                return str(m.content).lower() == "cancel" \
                       or (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id)

            msg_time = await self.client.wait_for('message', check=check, timeout=600)

            loop.create_task(self.delete_message(msg_time, 60))

            if str(msg_time.content).lower() == "cancel":
                await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                     "Nothing has been **added**", 30)
                os.remove(config.path + '/' + msg_name.content + '.mp3')
                break

            begin_times, end_times, is_valid_format = await self.valid_format(self, ctx, msg_time, file_duration)

            if not is_valid_format:
                continue

            if 0 <= end_times - begin_times <= 10:
                await self.embed_msg(ctx, f"I'm working on your file",
                                     "Please wait a few seconds", 60)
                file = AudioSegment.from_file(f"{config.path}/{msg_name.content}.mp3")
                file_trim = file[begin_times * 1000:end_times * 1000]
                file_trim.export(f"{config.path}/{msg_name.content}_trim.mp3", format="mp3")

                await ctx.send(file=discord.File(fp=f"{config.path}/{msg_name.content}_trim.mp3",
                                                 filename=f"{msg_name.content}_trim.mp3"), delete_after=60)
                await self.embed_msg(ctx, f"Would you like to keep this file?",
                                     "Type **yes** to keep it or **no** to cut it again, or **cancel**", 60)
                while True:
                    def check(m):
                        return str(m.content).lower() == "cancel" \
                               or str(m.content).lower() in "yes" \
                               or str(m.content).lower() in "no" \
                               or (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id)

                    msg_confirm = await self.client.wait_for('message', check=check, timeout=600)

                    loop.create_task(self.delete_message(msg_confirm, 60))

                    is_confirmed, is_no = await self.confirm_file(self, ctx, arg, msg_confirm, msg_name)

                    if is_confirmed or is_no:
                        break

                if is_confirmed:
                    break
                elif is_no:
                    continue

            else:
                await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                     "The file duration is longer than 10 seconds or lower than 0, please try again",
                                     60)

    @commands.command(aliases=['a', 'Add'])
    async def add(self, ctx, arg: str = None):

        # Discord async loop
        loop = self.client.loop or asyncio.get_event_loop()

        # Check if member has required role
        has_role = await self.required_role(self, ctx)

        if not has_role:
            return

        # Embed message to member
        await self.embed_msg(ctx, f"Hi {ctx.message.author.name}! Glad to see you :heart_eyes:",
                             "Please, upload an **audio** file, **youtube link** or type **cancel**", 30)

        # Function to check message content
        def check(m):
            return (str(m.content).lower() == "cancel" or m.attachments or
                    'youtube' in m.content or 'youtu.be' in m.content) \
                   and (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id)

        try:
            # Waiting for a message with check
            msg = await self.client.wait_for('message', check=check, timeout=600)

            # Command cancelled by member
            if str(msg.content).lower() == "cancel":
                await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                     "Nothing has been **added**", 30)
                loop.create_task(self.delete_message(msg, 30))
                return

            # Member sent a youtube link
            if 'youtube' in msg.content or 'youtu.be' in msg.content:
                loop.create_task(self.delete_message(msg, 60))

                await self.embed_msg(ctx, f"Processing file... :gear: :tools:",
                                     "Please wait a few seconds :hourglass:", 60)

                # Download, convert to mp3 and get info about file
                file_title, file_duration = await self.get_file_info(self, ctx, msg.content)

                if file_title is None or file_duration is None:
                    return

                await self.link_file(self, ctx, arg, file_title, file_duration, loop)

                return

            headers = {
                'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
            }

            request_msg = requests.get(msg.attachments[0].url, headers=headers, stream=False)
            filename = msg.attachments[0].filename
            mp3 = filename.split('.')
            path = f"{config.path}/{filename}"

            if mp3[len(mp3) - 1] == "mp3":
                async with ctx.typing():
                    fn = functools.partial(self.add_song, path, request_msg)
                    await loop.run_in_executor(None, fn)

                audio = mutagen.File(path)

                hashcode = hashlib.md5(open(path, 'rb').read()).hexdigest()

                if int(audio.info.length) < 10:
                    await self.insert_file_db(self, ctx, arg, filename, hashcode)
                    os.rename(path, f"{config.path}/{hashcode}.mp3")
                else:
                    await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                         f"**{filename}** is longer than 10 seconds, **wavU** could not add it", 60)
                    os.remove(path)
            else:
                await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                     f"This is not a **.mp3** file, **wavU** could not add it", 30)
            loop.create_task(self.delete_message(msg, 30))

        except asyncio.TimeoutError:
            await ctx.send('Timeout!', delete_after=15)
            await asyncio.sleep(15)
            await ctx.message.delete()


def setup(client):
    client.add_cog(AddCommand(client))
