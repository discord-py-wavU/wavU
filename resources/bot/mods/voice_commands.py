# -*- coding: utf-8 -*-

import asyncio
import logging

import discord
from discord.ext import commands
from discord.utils import get

import config
from resources.audio.models import AudioInServer, AudioInEntity
from resources.bot.helpers import Helpers, running_commands
from resources.entity.models import Entity
from resources.server.models import Server


class VoiceCommands(commands.Cog, Helpers):

    def __init__(self, client):
        super().__init__()
        self.client = client

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

        is_connected = after.channel is not None and before.channel is not member.voice.channel
        not_wavu = member != self.client.user
        not_another_bot = not member.bot
        move_from_channel = before.channel and before.channel.guild is after.channel.guild

        try:

            if is_connected and not_wavu and not_another_bot and not move_from_channel:

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
                    obj_audio = await self.get_object(self, query_obj, {'audio__hashcode': audio.hashcode, 'enabled': True})

                if obj_audio:
                    path = f"{config.path}/{audio.hashcode}.mp3"

                    voice = get(self.client.voice_clients, guild=member.guild)
                    voice = await self.connect(voice, after)
                    if str(member.guild.id) not in self.queue:
                        await self.start_playing(self, voice, member, path, obj_audio)
                    else:
                        self.queue[str(member.guild.id)].append((path, obj_audio))
        except Exception as e:
            logging.warn(f"Unexpected error {e}")
            voice = get(self.client.voice_clients, guild=member.guild)
            if voice and voice.is_connected():
                await voice.disconnect()

    @commands.command(aliases=['Choose', 'ch', 'c', 'Ch', 'C'])
    async def choose(self, ctx, arg=None):

        if not await self.check_if_running(self, ctx):
            return

        loop = self.client.loop or asyncio.get_event_loop()

        if ctx.author.voice is None:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                 "You need to be connected on a **Voice channel**", 30)
            running_commands.remove(ctx.author)
            return

        valid, discord_id, obj_type = await self.valid_arg(self, ctx, arg)
        if not valid:
            running_commands.remove(ctx.author)
            return

        obj, audios, hashcodes = await self.search_songs(self, ctx, arg)

        if audios:
            actual_page = 0
            self.actual_page = 0

            self.list_audios = [audios[i:i + 10] for i in range(0, len(audios), 10)]
            self.page_len = len(self.list_audios)

            msg = f"Choose a number to play a file\n"
            emb_msg = await self.show_audio_list(self, ctx, self.list_audios[0], msg)

            def check(reaction, user):
                return user != self.client.user and user.guild.id == ctx.guild.id

            task_core_reaction = loop.create_task(self.core_reactions(self, emb_msg, actual_page))

            try:
                while True:
                    reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=600)
                    if reaction:
                        await asyncio.sleep(0.1)
                        await emb_msg.remove_reaction(emoji=reaction.emoji, member=user)

                    if user.id != ctx.message.author.id:
                        continue

                    if str(reaction.emoji) == "➡️" or str(reaction.emoji) == "⬅️":
                        if actual_page:
                            await actual_page
                        if task_core_reaction is not None:
                            await task_core_reaction

                        actual_page = loop.create_task(self.arrows_reactions(self, emb_msg, reaction, msg))

                    if str(reaction.emoji) in self.dict_numbers:
                        offset = (self.actual_page * 10) + int(self.dict_numbers[str(reaction.emoji)]) - 1
                        try:
                            audio_to_play = f"{config.path}/{hashcodes[offset]}.mp3"
                            volume_obj = obj[offset]
                        except IndexError as IE:
                            logging.warning(IE)
                            continue
                        try:
                            if str(ctx.guild.id) not in self.queue:
                                channel = ctx.author.voice.channel
                                voice = await channel.connect()
                                loop.create_task(self.start_playing(self, voice, ctx.author, audio_to_play, volume_obj))
                            else:
                                self.queue[str(ctx.guild.id)].append((audio_to_play, volume_obj))
                        except discord.ClientException as e:
                            logging.warning(str(e))
                            await asyncio.sleep(1)
                            self.queue[str(ctx.guild.id)].append((audio_to_play, volume_obj))
                    elif str(reaction.emoji) == '❌':
                        await emb_msg.delete()
                        embed = discord.Embed(title=f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                              color=0xFC65E1)
                        await ctx.send(embed=embed, delete_after=10)
                        running_commands.remove(ctx.author)
                        return

            except asyncio.TimeoutError:
                await self.embed_msg(ctx, f"Timeout!",
                                     'This command was cancelled', 600)
                await emb_msg.delete()
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                 'List is empty')
        running_commands.remove(ctx.author)

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


async def setup(client):
    await client.add_cog(VoiceCommands(client))
