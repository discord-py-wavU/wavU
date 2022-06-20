import asyncio
import functools
import logging
import random
from os import listdir
from os.path import isfile, join
from pymongo import MongoClient

import discord
from discord.ext import commands
from discord.utils import get

import config


class VoiceCommands(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.queue = {}
        mongo_url = config.mongo
        cluster = MongoClient(mongo_url)
        db = cluster["main"]
        self.files_collection = db["files"]

    @staticmethod
    async def connect(voice, after):

        if voice and voice.is_connected():
            while voice.is_playing():
                await asyncio.sleep(0.1)
            await voice.move_to(after.channel)
        else:
            try:
                voice = await after.channel.connect()
            except discord.ClientException as e:
                logging.exception(str(e))
                await asyncio.sleep(1)

        return voice

    @staticmethod
    def search(path):
        try:
            audios_to_play = [f for f in listdir(path) if isfile(join(path, f)) and '.mp3' in f]
        except:
            audios_to_play = []

        return audios_to_play

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        if after.channel is not None and before.channel is not member.voice.channel and member != self.client.user and \
                not member.bot:

            audios = self.files_collection.find({"guild_id": member.guild.id, "user_id": member.id})

            audios = list(audios)

            if not len(audios):
                audios = self.files_collection.find({"guild_id": member.guild.id, "user_id": 0})
                audios = list(audios)

            audios_to_play = audios

            audio = random.choice(audios_to_play)

            path = f"audio/{member.guild.id}/{audio['audio_name']}"

            if audios:
                voice = get(self.client.voice_clients, guild=member.guild)
                voice = await self.connect(voice, after)
                if str(member.guild.id) not in self.queue:
                    await self.start_playing(self, voice, member, path)
                else:
                    self.queue[str(member.guild.id)].append(path)
        elif after.channel is None and len(before.channel.members) == 1:
            voice = get(self.client.voice_clients, guild=member.guild)
            if voice and voice.is_connected():
                await voice.disconnect()

    @staticmethod
    async def start_playing(self, voice, member, path_to_play):
        loop = self.client.loop or asyncio.get_event_loop()
        self.queue[str(member.guild.id)] = [path_to_play]

        i = 0
        avoid = 0
        while i < len(self.queue[str(member.guild.id)]) and avoid < 3:
            try:
                partial = functools.partial(voice.play, discord.FFmpegPCMAudio(self.queue[str(member.guild.id)][i]))
                await loop.run_in_executor(None, partial)
                while voice.is_playing():
                    await asyncio.sleep(1)
                i += 1
                avoid = 0
            except discord.ClientException as e:
                logging.exception(str(e))
                await asyncio.sleep(1)
                avoid += 1

        del self.queue[str(member.guild.id)]
        await asyncio.sleep(1)
        await voice.disconnect()

    @staticmethod
    async def search_songs(self, ctx, arg):

        if arg is None:
            audios = self.files_collection.find({"guild_id": ctx.message.guild.id, "user_id": 0})
        else:
            audios = self.files_collection.find({"guild_id": ctx.message.guild.id, "user_id": ctx.message.author.id})
        audios = list(audios)

        songs = list(map(lambda audio: audio["audio_name"], audios))

        return songs

    @staticmethod
    async def delete_message(msg):
        await asyncio.sleep(30)
        await msg.delete()

    @staticmethod
    async def embed_msg(ctx, name, value, delete=None):
        embed = discord.Embed(color=0xFC65E1)
        embed.add_field(name=name,
                        value=value,
                        inline=False)
        await ctx.send(embed=embed, delete_after=delete)

    @commands.command(aliases=['Choose', 'ch', 'c', 'Ch', 'C'])
    async def choose(self, ctx, arg=None):

        if ctx.author.voice is None:
            await ctx.send("You need to be connected on a **Voice channel**")
            return

        loop = self.client.loop or asyncio.get_event_loop()

        songs = await self.search_songs(self, ctx, arg)

        if songs:
            list_songs = ""
            for index, song in enumerate(songs):
                list_songs = list_songs + str(index + 1) + ". " + song.split(".mp3")[0] + "\n"
            list_songs = list_songs + "cancel"
            await ctx.send("List .mp3 files:\n" + list_songs, delete_after=30)
            await ctx.send("Choose a number to play a _**.mp3**_ file or _**cancel**_", delete_after=30)

            await self.embed_msg(ctx, f"List .mp3 files:",
                                 "Nothing has been **added**", 30)

            def check(m):
                return (m.content.isdigit() and
                        m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                       or m.content == "cancel" or m.content == "Cancel"

            try:
                for i in range(3):
                    msg = await self.client.wait_for('message', check=check, timeout=30)
                    if msg.content.isdigit() and int(msg.content) <= len(songs) and int(msg.content) != 0:

                        await ctx.send("**" + songs[int(msg.content) - 1] + '** was chosen')
                        audio_to_play = f"audio/{ctx.message.guild.id}/{songs[int(msg.content) - 1]}"

                        try:
                            if str(ctx.guild.id) not in self.queue:
                                channel = ctx.author.voice.channel
                                voice = await channel.connect()
                                await self.start_playing(self, voice, ctx.author, audio_to_play)
                            else:
                                self.queue[str(ctx.guild.id)].append(audio_to_play)
                        except discord.ClientException as e:
                            logging.exception(str(e))
                            await asyncio.sleep(1)
                            self.queue[str(ctx.guild.id)].append(audio_to_play)
                        break
                    elif msg.content == "cancel" or msg.content == "Cancel":
                        await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                             "Nothing has been **chosen**", 30)
                        loop.create_task(self.delete_message(msg))
                        break
                    elif int(msg.content) > len(songs) or int(msg.content) == 0:
                        await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                             f'That number is not an option. Try again **({str(i + 1)}"/3)**', 10)
                        await ctx.send("That number is not an option. Try again **(" + str(i + 1) + "/3)**",
                                       delete_after=10)
                        loop.create_task(self.delete_message(msg))
                        if i == 2:
                            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                                 'None of the attempts were correct, wavU could not choose any file')
            except asyncio.TimeoutError:
                await self.embed_msg(ctx, f"Timeout!",
                                     'This command was cancelled', 15)
                await asyncio.sleep(15)
                await ctx.message.delete()
        else:
            await ctx.send("_List is empty_")

    @commands.command(aliases=['shutup', 'disconnect', 'disc', 'Shutup', 'Stop', 'Disconnect', 'Disc'])
    async def stop(self, ctx):
        if ctx.voice_client is not None and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await self.embed_msg(ctx, f"Bye {ctx.message.author.name}",
                                 '**wavU** was stopped and disconnected')
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}!",
                                 '**wavU** is not connected')


def setup(client):
    client.add_cog(VoiceCommands(client))
