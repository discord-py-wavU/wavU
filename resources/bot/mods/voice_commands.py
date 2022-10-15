import asyncio
import functools
import logging

import discord
from discord.ext import commands
from discord.utils import get

import config
from resources.audio.models import AudioInServer, AudioInEntity
from resources.bot.helpers import Helpers
from resources.entity.models import Entity
from resources.server.models import Server


class VoiceCommands(commands.Cog, Helpers):

    def __init__(self, client):
        self.client = client
        self.queue = {}

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

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        if after.channel is not None and before.channel is not member.voice.channel and member != self.client.user and \
                not member.bot:

            # Check first personal audios
            audio, obj = await self.get_async_audio(self, Entity, {"discord_id": member.id,
                                                                   'audios__enabled': True,
                                                                   'server__discord_id': member.guild.id})

            # Second check channel audios
            if not audio:
                audio, obj = await self.get_async_audio(self, Entity, {"discord_id": member.voice.channel.id,
                                                                       'audios__enabled': True,
                                                                       'server__discord_id': member.guild.id})

            query_obj = AudioInEntity

            # Third check server audios
            if not audio:
                audio, obj = await self.get_async_audio(self, Server, {"discord_id": member.guild.id, 'enabled': True})
                query_obj = AudioInServer

            obj_audio = None

            if audio:
                obj_audio = await self.get_object(query_obj, {'audio__hashcode': audio.hashcode})

            path = f"{config.path}/{audio.hashcode}.mp3"

            if audio:
                voice = get(self.client.voice_clients, guild=member.guild)
                voice = await self.connect(voice, after)
                if str(member.guild.id) not in self.queue:
                    await self.start_playing(self, voice, member, path, obj_audio)
                else:
                    self.queue[str(member.guild.id)].append((path, obj_audio))
        elif after.channel is None and len(before.channel.members) == 1:
            voice = get(self.client.voice_clients, guild=member.guild)
            if voice and voice.is_connected():
                await voice.disconnect()

    @staticmethod
    async def start_playing(self, voice, member, path_to_play, obj_audio):
        loop = self.client.loop or asyncio.get_event_loop()
        self.queue[str(member.guild.id)] = [(path_to_play, obj_audio)]

        i = 0
        avoid = 0
        while i < len(self.queue[str(member.guild.id)]) and avoid < 3:
            try:
                volume = int(self.queue[str(member.guild.id)][i][1].volume) / 100
                audio = self.queue[str(member.guild.id)][i][0]
                partial = functools.partial(voice.play,
                                            discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(audio), volume=volume))
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

    @commands.command(aliases=['Choose', 'ch', 'c', 'Ch', 'C'])
    async def choose(self, ctx, arg=None):

        if ctx.author.voice is None:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                 "You need to be connected on a **Voice channel**", 30)
            return

        loop = self.client.loop or asyncio.get_event_loop()

        obj, audios, hashcodes = await self.search_songs(self, ctx, arg)

        volume_obj = await obj.afirst()

        if audios:
            msg = f"Choose a number to play a _**.mp3**_ file or _**cancel**_\n"
            await self.show_audio_list(self, ctx, audios, msg)

            def check(m):
                return (m.content.isdigit() and
                        m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                       or str(m.content).lower() == "cancel"

            try:
                for i in range(3):
                    msg = await self.client.wait_for('message', check=check, timeout=30)
                    if msg.content.isdigit() and int(msg.content) <= len(audios) and int(msg.content) != 0:

                        await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                             "**" + audios[int(msg.content) - 1] + '** was chosen', 30)
                        audio_to_play = f"{config.path}/{hashcodes[int(msg.content) - 1]}.mp3"
                        try:
                            if str(ctx.guild.id) not in self.queue:
                                channel = ctx.author.voice.channel
                                voice = await channel.connect()
                                await self.start_playing(self, voice, ctx.author, audio_to_play, volume_obj)
                            else:
                                self.queue[str(ctx.guild.id)].append(audio_to_play)
                        except discord.ClientException as e:
                            logging.exception(str(e))
                            await asyncio.sleep(1)
                            self.queue[str(ctx.guild.id)].append(audio_to_play)
                        break
                    elif str(msg.content).lower() == "cancel":
                        await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                             "Nothing has been **chosen**", 30)
                        loop.create_task(self.delete_message(msg))
                        break
                    elif int(msg.content) > len(audios) or int(msg.content) == 0:
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
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                 'List is empty')

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
