# -*- coding: utf-8 -*-

import asyncio
import functools
import logging
import re

import discord
from asgiref.sync import sync_to_async

import config
from resources.audio.models import Audio, AudioInEntity, AudioInServer
from resources.entity.models import Entity
from resources.server.models import Server

running_commands = set()


class Helpers:

    def __init__(self):
        self.queue = {}
        self.list_audios = []
        self.page_len = 0
        self.actual_page = 0
        self.dict_numbers = {'1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣', '5': '5️⃣',
                             '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣', '10': '🔟',
                             '1️⃣': '1', '2️⃣': '2', '3️⃣': '3', '4️⃣': '4', '5️⃣': '5',
                             '6️⃣': '6', '7️⃣': '7', '8️⃣': '8', '9️⃣': '9', '🔟': '10'}

    @staticmethod
    async def get_or_create_object(obj, kwargs, default=None):
        return await sync_to_async(obj.objects.get_or_create, thread_sensitive=True)(**kwargs, defaults=default)

    @staticmethod
    async def filter_object(obj, kwargs):
        return await sync_to_async(obj.objects.filter, thread_sensitive=True)(**kwargs)

    @staticmethod
    async def get_object(self, obj, kwargs):
        try:
            objects = await self.filter_object(obj, kwargs)
            gotten_obj = await sync_to_async(lambda: objects.distinct().first(), thread_sensitive=True)()
        except Exception as e:
            print(e)
            gotten_obj = None
        return gotten_obj

    @staticmethod
    async def get_random_object(obj):
        return await sync_to_async(obj.objects.order_by('?').first(), thread_sensitive=True)()

    @staticmethod
    async def get_async_audio(self, async_obj, kwargs):
        objects = await self.filter_object(async_obj, kwargs)
        obj = await sync_to_async(lambda: objects.distinct().first(), thread_sensitive=True)()
        if obj:
            obj_audio = await obj.audios.order_by('?').afirst()
            return await sync_to_async(lambda: obj_audio.audio, thread_sensitive=True)(), objects
        return None, None

    @staticmethod
    async def get_async_audio_list(self, async_obj, kwargs):
        audio_name_list = []
        audio_hashcode_list = []
        objects = await self.filter_object(async_obj, kwargs)
        async for obj in objects:
            audio_name_list.append(obj.name)
            hashcode = await sync_to_async(lambda: obj.audio.hashcode, thread_sensitive=True)()
            audio_hashcode_list.append(hashcode)
        return objects, audio_name_list, audio_hashcode_list

    @staticmethod
    async def search_songs(self, ctx, arg):

        server = await self.get_object(self, Server, {'discord_id': ctx.message.guild.id})
        is_server = False
        discord_id = 0

        if arg:
            discord_id = await self.get_id_from_mention(arg, discord_id)
            is_server = self.client.get_guild(int(discord_id))

        if arg is None or is_server:
            obj, audio_name_list, audio_hashcode_list = await \
                self.get_async_audio_list(self, AudioInServer, {'server': server})
        else:
            entity, _ = await self.get_or_create_object(Entity, {'discord_id': discord_id, 'server': server})
            obj, audio_name_list, audio_hashcode_list = await \
                self.get_async_audio_list(self, AudioInEntity, {'entity': entity})

        return obj, audio_name_list, audio_hashcode_list

    @staticmethod
    async def show_audio_list(self, ctx, audios, msg):
        list_songs = ""
        for index, song in enumerate(audios):
            list_songs = list_songs + f"{str(index + 1)}. {song}\n"
        list_songs = f"{list_songs}cancel"
        return await self.embed_msg(ctx, f"List .mp3 files:", f"{msg}{list_songs}")

    @staticmethod
    async def required_role(self, ctx, guild=None):

        if not guild:
            roles = ctx.message.author.roles
            msg = f"You need _**FM**_ role to use this command.\n"
        else:
            roles = guild.get_member(ctx.message.author.id).roles
            msg = f"You need _**FM**_ role on _**{guild.name}**_ to use this command.\n"

        has_role = True
        if "FM" not in (roles.name for roles in roles):
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:", msg +
                                 "Only members who have administrator permissions are able to assign _**FM**_ role.\n"
                                 f"Command: \"**{config.prefix} role @mention**\"")
            has_role = False
            running_commands.remove(ctx.author)

        return has_role

    @staticmethod
    async def get_mentions(mentions):
        discord_ids = []
        for mention in mentions:
            discord_ids.append(mention.id)
        return discord_ids

    @staticmethod
    async def valid_amount_mentions(self, ctx, n):
        valid = True
        if len(ctx.message.mentions) > n:
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 f"There are more than {n} mention on this message, please try again", 30)
            valid = False
        return valid

    @staticmethod
    async def get_id_from_mention(mention, discord_id):
        value = re.findall(r'\b\d+\b', mention)
        if value:
            discord_id = int(value[0])
        return discord_id

    @staticmethod
    async def valid_person(self, ctx, arg, discord_id):
        obj_type = None
        discord_id = await self.get_id_from_mention(arg, discord_id)
        valid = ctx.guild.get_member(discord_id)
        if not valid:
            discord_id = None
        else:
            obj_type = "Member"
        return valid, discord_id, obj_type

    @staticmethod
    async def valid_channel(self, ctx, arg, server_id, discord_id):
        discord_id = await self.get_id_from_mention(arg, discord_id)
        valid = True
        if not server_id:
            server_id = ctx.guild.id
        guild = self.client.get_guild(server_id)
        voice_channels = guild.voice_channels
        name_channels_list = [voice_channel.name for voice_channel in voice_channels]
        if arg not in name_channels_list and not arg.isdigit():
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 f"This argument ({arg}) is not valid, please try again", 30)
            valid = False
        else:
            if arg.isdigit():
                channel = guild.get_channel(int(arg))
                if channel:
                    discord_id = channel.id
                else:
                    discord_id = None
            else:
                discord_id = voice_channels[name_channels_list.index(arg)].id
            if not discord_id:
                await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                     f"This argument ({arg}) is not a valid id, please try again", 30)
                valid = False

        return valid, discord_id

    @staticmethod
    async def valid_arg(self, ctx, arg, server_id=None):
        if arg:
            name_channels_list = []
            discord_id = None
            valid, discord_id, obj_type = await self.valid_person(self, ctx, arg, discord_id)

            if not valid and arg.isdigit():
                valid = self.client.get_guild(int(arg))
                if valid:
                    discord_id = valid.id
                    obj_type = "Server"

            if not valid:
                valid, discord_id = await self.valid_channel(self, ctx, arg, server_id, discord_id)
                if valid:
                    obj_type = "Channel"
            if str(discord_id) not in arg and name_channels_list and arg not in name_channels_list:
                await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                     f"This format is wrong, please use **{config.prefix}help**", 30)
                valid = False
                obj_type = ""
                running_commands.remove(ctx.author)
        else:
            valid = True
            discord_id = ctx.message.guild.id
            obj_type = "Server"

        return valid, discord_id, obj_type

    @staticmethod
    async def valid_server(self, ctx, arg):
        discord_id = None
        if arg.isdigit():
            guild = self.client.get_guild(int(arg))
            if guild:
                return True, guild.id
        else:

            guilds = self.client.guilds
            name_guilds_list = [guild.name for guild in guilds]
            if arg not in name_guilds_list:
                await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                     f"This is not a guild name, please try again", 30)
                return False, discord_id
            else:
                discord_id = guilds[name_guilds_list.index(arg)].id
            if not discord_id:
                await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                     f"This guild id isn't valid, please try again", 30)
                return False, discord_id

        return True, discord_id

    @staticmethod
    async def insert_file_db(self, ctx, arg: str, filename: str, hashcode: str, discord_id):

        audio, _ = await self.get_or_create_object(Audio, {'hashcode': hashcode})
        server, _ = await self.get_or_create_object(Server, {'discord_id': ctx.message.guild.id})

        print(filename)

        if arg is None:
            audio, created = await self.get_or_create_object(AudioInServer,
                                                             {'audio': audio, 'server': server}, {'name': filename})
        else:
            entity, _ = await self.get_or_create_object(Entity, {'discord_id': discord_id, 'server': server})
            audio, created = await self.get_or_create_object(AudioInEntity,
                                                             {'audio': audio, 'entity': entity}, {'name': filename})

        if created:
            await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                 f"**{filename}** was added to **{ctx.message.guild.name}**")

            print(f"{ctx.message.author.name} ({ctx.message.author.id}) added "
                  f"{filename} to {ctx.message.guild.name} ({ctx.message.guild.id})")

        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                 f"You already have **{filename}** in **{ctx.message.guild.name} **")

            print(f"{ctx.message.author.name} ({ctx.message.author.id}) tried to added "
                  f"{filename} to {ctx.message.guild.name} ({ctx.message.guild.id}) but already exists")
        print(f"Hashcode: {hashcode}, Audio_id: {audio.id}")

    @staticmethod
    async def delete_message(msg, time: int):
        await asyncio.sleep(time)
        await msg.delete()

    @staticmethod
    async def embed_msg(ctx, name: str, value: str, delete: int = None):
        embed = discord.Embed(color=0xFC65E1)
        embed.add_field(name=name,
                        value=value,
                        inline=False)
        return await ctx.send(embed=embed, delete_after=delete)

    @staticmethod
    def add_song(path, r):
        with open(path, 'wb') as f:
            for chunk in r.iter_content():
                if chunk:
                    f.write(chunk)
        f.close()

    @staticmethod
    async def show_status_list(self, ctx, objects):
        list_songs = ""
        for index, obj in enumerate(objects):
            emoji = ":white_check_mark:" if obj[1] else ":x:"
            list_songs = list_songs + f"{str(index + 1)}. {obj[0]} {emoji}\n"
        if list_songs:
            return await self.embed_msg(ctx, f"List .mp3 files:", f"{list_songs}")

    @staticmethod
    async def edit_status_message(emb_msg, msg, objects):
        list_songs = ""
        for index, obj in enumerate(objects):
            emoji = ":white_check_mark:" if obj[1] else ":x:"
            list_songs = list_songs + f"{str(index + 1)}. {obj[0]} {emoji}\n"
        embed = discord.Embed(color=0xFC65E1)
        embed.add_field(name=f"List .mp3 files:",
                        value=f"{msg}{list_songs}",
                        inline=False)

        await emb_msg.edit(embed=embed)

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

    @staticmethod
    async def edit_message(self, emb_msg, msg):
        list_songs = ""
        for index, song in enumerate(self.list_audios[self.actual_page]):
            list_songs = list_songs + f"{str(index + 1)}. {song}\n"
        list_songs = f"{list_songs}cancel"
        embed = discord.Embed(color=0xFC65E1)
        embed.add_field(name=f"List .mp3 files:",
                        value=f"{msg}{list_songs}",
                        inline=False)

        await emb_msg.edit(embed=embed)

    @staticmethod
    async def arrows_reactions(self, emb_msg, reaction, msg, out_of_range=False, edit_status=False):

        prev = self.list_audios[self.actual_page]

        if str(reaction.emoji) == "➡️":
            self.actual_page = (self.actual_page + 1) % self.page_len
        elif str(reaction.emoji) == "⬅️" or out_of_range:
            self.actual_page = (self.actual_page - 1) % self.page_len

        actual = self.list_audios[self.actual_page]

        if edit_status:
            await self.edit_status_message(emb_msg, msg, self.list_audios[self.actual_page])
        else:
            await self.edit_message(self, emb_msg, msg)

        if len(actual) < len(prev):
            remove = len(prev) - len(actual)
            for ind in range(remove):
                await asyncio.sleep(0.1)
                await emb_msg.remove_reaction(emoji=self.dict_numbers[str(len(prev) - ind)], member=self.client.user)
        else:
            add = len(actual) - len(prev)
            for ind in range(add):
                await asyncio.sleep(0.1)
                await emb_msg.add_reaction(self.dict_numbers[str(len(prev) + ind + 1)])

        return actual

    @staticmethod
    async def core_reactions(self, msg_em, actual_page):

        await msg_em.add_reaction('⬅️')
        await msg_em.add_reaction('❌')
        await msg_em.add_reaction('➡️')

        for ind in range(len(self.list_audios[actual_page])):
            await msg_em.add_reaction(self.dict_numbers[str(ind + 1)])
            await asyncio.sleep(0.1)

    @staticmethod
    async def check_if_running(self, ctx):
        # Check if the user is in the set of running commands
        if ctx.author in running_commands:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name} ",
                                 "You cannot use more than one command at once, "
                                 "please finish or cancel your current process", 30)
            # Return False if the user is already running a command
            return False
        else:
            # Add the user to the set of running commands
            running_commands.add(ctx.author)

            # Return True if the user is not already running a command
            return True

    @staticmethod
    async def delete_embed_message(ctx, emb_msg):
        await emb_msg.delete()
        embed = discord.Embed(title=f"Thanks {ctx.message.author.name} for using wavU :wave:",
                              color=0xFC65E1)
        await ctx.send(embed=embed, delete_after=10)
