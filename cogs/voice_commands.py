import random
import config
from datetime import datetime
import asyncio
import functools

import discord
from discord.ext import commands
from discord.utils import get
from cogs import db

from os import listdir
from os.path import isfile, join


class VoiceCommands(commands.Cog):

    def __init__(self, client):
        self.client = client

    @staticmethod
    def check_db(member):
        servers = db.all_servers(False)
        is_on = True
        for server in servers:
            if str(member.guild.name) == server[1] and server[2] == 0:
                is_on = False

        return is_on

    @staticmethod
    async def connect(voice, after):

        if voice and voice.is_connected():
            await voice.move_to(after.channel)
        else:
            voice = await after.channel.connect()

        return voice

    @staticmethod
    async def search_song(self, path, member, after):

        is_Empty = True
        is_on = self.check_db(member)
        audio_to_play = []
        voice = get(self.client.voice_clients, guild=member.guild)

        if is_on:
            try:
                member_path = path + '/' + str(member)
                audios_to_play = [f for f in listdir(member_path) if isfile(join(member_path, f)) and '.mp3' in f]
            except Exception as e:
                print(str(e))
                audios_to_play = []

            if not audios_to_play:
                try:
                    audios_to_play = [f for f in listdir(path) if isfile(join(path, f)) and '.mp3' in f]
                except Exception as e:
                    print(str(e))
                    audios_to_play = []
                if audios_to_play:
                    print("hi")
                    is_Empty = False
                    voice = await self.connect(voice, after)
                    audio_to_play = 'audio/' + member.guild.name + '/' + random.choice(audios_to_play)
            elif audios_to_play:
                is_Empty = False
                voice = await self.connect(voice, after)
                audio_to_play = 'audio/' + member.guild.name + '/' \
                                + str(member) + '/' + random.choice(audios_to_play)

        return audio_to_play, voice, is_Empty

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        loop = self.client.loop or asyncio.get_event_loop()
        path = config.path + '/' + member.guild.name
        if after.channel is not None and before.channel is not member.voice.channel and member != self.client.user:

            audio_to_play, voice, is_Empty = await self.search_song(self, path, member, after)

            if not is_Empty:
                try:
                    if not voice.is_playing():
                        partial = functools.partial(voice.play, discord.FFmpegPCMAudio(audio_to_play))
                        await loop.run_in_executor(None, partial)
                        await asyncio.sleep(2)
                    else:
                        while voice.is_playing():
                            await asyncio.sleep(0.5)
                        partial = functools.partial(voice.play, discord.FFmpegPCMAudio(audio_to_play))
                        await loop.run_in_executor(None, partial)
                        await asyncio.sleep(0.5)

                    while voice.is_playing():
                        await asyncio.sleep(1)

                    if voice.is_connected() and not voice.is_playing():
                        await voice.disconnect()

                except discord.ClientException as e:
                    print("Error: " + str(e))
        elif after.channel is None and len(before.channel.members) == 1:
            voice = get(self.client.voice_clients)
            if voice and voice.is_connected():
                await voice.disconnect()

    @staticmethod
    async def search_songs(ctx, arg):
        if arg is not None:
            path = config.path + "/" + ctx.message.guild.name + '/' + str(ctx.message.mentions[0])
        else:
            path = config.path + "/" + ctx.message.guild.name
        try:
            songs = [f for f in listdir(path) if isfile(join(path, f)) and '.mp3' in f]
        except Exception as e:
            print(str(e))
            songs = []

        return songs

    @commands.command(aliases=['ch', 'c'], help='Play a chosen .mp3 file')
    async def choose(self, ctx, arg=None):
        loop = self.client.loop or asyncio.get_event_loop()

        songs = await self.search_songs(ctx, arg)

        if songs:
            list_songs = ""
            for index, song in enumerate(songs):
                list_songs = list_songs + str(index+1) + ". " + song.split(".mp3")[0] + "\n"
            list_songs = list_songs + "cancel"
            await ctx.send("List .mp3 files:\n" + list_songs, delete_after=30)
            await ctx.send("Choose a number to play a .mp3 file", delete_after=30)

            def check(m):
                return (m.content.isdigit() and m.author.guild.name == ctx.message.guild.name) \
                       or m.content == "cancel" or m.content == "Cancel"
            try:
                msg = await self.client.wait_for('message', check=check, timeout=30)

                if msg.content.isdigit() and int(msg.content) <= len(songs) and int(msg.content) != 0:
                    await ctx.send(songs[int(msg.content)-1] + ' is playing')
                    channel = ctx.author.voice.channel
                    voice = await channel.connect()
                    if arg is not None:
                        audio_to_play = 'audio/' + ctx.message.guild.name + '/' \
                                        + str(ctx.message.mentions[0]) + '/' + songs[int(msg.content)-1]
                    else:
                        audio_to_play = 'audio/' + ctx.message.guild.name + '/' + songs[int(msg.content)-1]

                    if not voice.is_playing():
                        partial = functools.partial(voice.play, discord.FFmpegPCMAudio(audio_to_play))
                        await loop.run_in_executor(None, partial)

                    else:
                        while voice.is_playing():
                            await asyncio.sleep(0.5)
                        partial = functools.partial(voice.play, discord.FFmpegPCMAudio(audio_to_play))
                        await loop.run_in_executor(None, partial)
                        await asyncio.sleep(0.5)

                    while voice.is_playing():
                        await asyncio.sleep(1)

                    if voice.is_connected() and not voice.is_playing():
                        await voice.disconnect()
                        await msg.delete()

                elif msg.content == "cancel" or msg.content == "Cancel":
                    await ctx.send("Nothing has been chosen")
                    await msg.delete()
                elif int(msg.content) > len(songs) or int(msg.content) == 0:
                    await ctx.send("That number is not an option")
                    await msg.delete()
            except asyncio.TimeoutError:
                await ctx.send('Timeout!', delete_after=15)
                await asyncio.sleep(15)
                await ctx.message.delete()
        else:
            await ctx.send("List is empty")

    @commands.command()
    @commands.has_role('PepeMaster')
    async def time(self):
        print(get_current_time())


def get_current_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time


def setup(client):
    client.add_cog(VoiceCommands(client))
