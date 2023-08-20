# Standard imports
import asyncio
import logging
import functools
# Discord imports
import discord
from discord.ext import commands
from discord.utils import get
# Own imports
import config
import content
# Project imports
from resources.audio.models import AudioInServer, AudioInEntity
from resources.entity.models import Entity
from resources.server.models import Server
from resources.bot.command_base import CommandBase, RUNNING_COMMAND


class Voice:

    def __init__(self):
        super().__init__()

    async def start_playing(self, voice, member, path_to_play, obj_audio):
        loop = self.client.loop or asyncio.get_event_loop()
        self.queue[str(member.guild.id)] = [(path_to_play, obj_audio)]

        i = 0
        avoid = 0
        while i < len(self.queue[str(member.guild.id)]) and avoid < 3:
            try:
                volume = int(
                    self.queue[str(member.guild.id)][i][1].volume) / 100
                audio = self.queue[str(member.guild.id)][i][0]
                await asyncio.sleep(0.5)
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
                i += 1
                avoid += 1

        del self.queue[str(member.guild.id)]
        await asyncio.sleep(1)
        await voice.disconnect()


class VoiceCommands(commands.Cog, CommandBase, Voice):

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
        move_from_channel = before.channel and after.channel and before.channel.guild is after.channel.guild
        voice = get(self.client.voice_clients, guild=member.guild)

        try:

            if is_connected and not_wavu and not_another_bot and not move_from_channel:

                # Check first personal audios
                audio = await self.get_async_audio(
                    Entity,
                    {
                        "discord_id": member.id,
                        "audios__enabled": True,
                        "server__discord_id": member.guild.id
                    }
                )

                # Second check channel audios
                if not audio:
                    audio = await self.get_async_audio(
                        Entity,
                        {"discord_id": member.voice.channel.id,
                         "audios__enabled": True,
                         "server__discord_id": member.guild.id})

                query_obj = AudioInEntity

                # Third check server audios
                if not audio:
                    audio = await self.get_async_audio(
                        Server, {"discord_id": member.guild.id,
                                 'enabled': True}
                    )
                    query_obj = AudioInServer

                obj_audio = None

                if audio:
                    obj_audio = await self.get_object(
                        query_obj, {
                            'audio__hashcode': audio.hashcode, 'enabled': True}
                    )

                if obj_audio:
                    path = f"{config.path}/{audio.hashcode}.mp3"

                    voice = await self.connect(voice, after)
                    if str(member.guild.id) not in self.queue:
                        await self.start_playing(voice, member, path, obj_audio)
                    else:
                        self.queue[str(member.guild.id)].append(
                            (path, obj_audio))
            elif is_connected and not_wavu and not_another_bot and move_from_channel:
                if voice and voice.is_connected():
                    await voice.move_to(after.channel)
            elif after.channel is None and len(before.channel.members) == 1:
                if voice and voice.is_connected():
                    await voice.disconnect()
        except Exception as e:
            logging.warn(f"Unexpected error {e}")
            if voice and voice.is_connected() and after.channel is None:
                await voice.disconnect()

    @commands.command(aliases=['Choose', 'ch', 'c', 'Ch', 'C'])
    async def choose(self, ctx, arg=None):

        if not await self.user_input_valid(ctx, arg):
            return

        objects, audios, hashcodes = await self.get_audios(ctx, arg)

        loop = self.client.loop or asyncio.get_event_loop()

        if audios:
            self.actual_page = 0

            self.list_audios = [audios[i:i + 10]
                                for i in range(0, len(audios), 10)]
            self.page_len = len(self.list_audios)

            self.view = discord.ui.View()
            self.instruction_msg = f"Choose a number to play\n"
            await self.button_interactions()
            await self.show_audio_list(ctx)

            def check(user):
                return user != self.client.user and user.guild.id == ctx.guild.id

            try:
                while True:
                    btn = await self.client.wait_for('interaction', check=check, timeout=600)
                    await self.get_interaction(btn)

                    if self.interaction == 'right' or self.interaction == 'left':
                        await self.move_page(btn, ctx)

                    if isinstance(self.interaction, int):
                        try:
                            offset = (self.actual_page * 10) + self.interaction - 1
                            audio_to_play = f"{config.path}/{hashcodes[offset]}.mp3"
                            volume_obj = objects[offset]
                            await btn.response.defer()
                        except IndexError as IE:
                            logging.warning(IE)
                            continue
                        try:
                            if str(ctx.guild.id) not in self.queue:
                                channel = ctx.author.voice.channel
                                voice = await channel.connect()
                                loop.create_task(self.start_playing(
                                    voice, ctx.author, audio_to_play, volume_obj))
                            else:
                                self.queue[str(ctx.guild.id)].append(
                                    (audio_to_play, volume_obj))
                        except discord.ClientException as e:
                            logging.warning(str(e))
                            await asyncio.sleep(1)
                            self.queue[str(ctx.guild.id)].append(
                                (audio_to_play, volume_obj))
                    elif self.interaction == 'cancel':
                        await btn.response.defer()
                        await self.emb_msg.delete()
                        await self.add_special_buttons(ctx)
                        RUNNING_COMMAND.remove(ctx.author)
                        return

            except asyncio.TimeoutError:
                await self.embed_msg(ctx, f"Timeout!",
                                     'This command was cancelled', 600)
                await self.emb_msg.delete()
        else:
            username = ctx.message.author.name.capitalize()
            await self.embed_msg(ctx, content.hey_msg.format(username), content.empty_list)
        RUNNING_COMMAND.remove(ctx.author)

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
