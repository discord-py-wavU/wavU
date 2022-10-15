import asyncio
import re

import discord
from asgiref.sync import sync_to_async

import config
from resources.audio.models import Audio, AudioInEntity, AudioInServer
from resources.entity.models import Entity
from resources.server.models import Server


class Helpers:

    @staticmethod
    async def get_or_create_object(obj, kwargs, default=None):
        return await sync_to_async(obj.objects.get_or_create, thread_sensitive=True)(**kwargs, defaults=default)

    @staticmethod
    async def filter_object(obj, kwargs):
        return await sync_to_async(obj.objects.filter, thread_sensitive=True)(**kwargs)

    @staticmethod
    async def get_object(obj, kwargs):
        try:
            gotten_obj = await sync_to_async(obj.objects.get, thread_sensitive=True)(**kwargs)
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

        server = await self.get_object(Server, {'discord_id': ctx.message.guild.id})
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
            list_songs = list_songs + f"{str(index + 1)}. {song.split('.mp3')[0]}\n"
        list_songs = f"{list_songs}cancel"
        await self.embed_msg(ctx, f"List .mp3 files:", f"{msg}{list_songs}", 30)

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

        return has_role

    @staticmethod
    async def get_discord_tag(self, ctx, src, dest=None, server_obj=None):
        discord_id = src
        if not server_obj:
            server_obj = ctx.guild.id
        elif server_obj.isdigit():
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 'No valid argument, please try again.\n'
                                 "If your channel's name has spaces you need to use quotes\n"
                                 'ex.: "Channel with spaces"'
                                 f'\nType **{config.prefix}help** for more information', 30)
            return None

        mention = ctx.message.mentions
        if mention:
            discord_id = mention[0].id
        valid = ctx.guild.get_member(discord_id)
        if not valid:
            guilds = self.client.get_guild(server_obj)
            if guilds:
                voice_channels = guilds.voice_channels
                if src not in [voice_channel.name for voice_channel in voice_channels]:
                    discord_id = None
            else:
                discord_id = None

        return discord_id

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
                discord_id = voice_channels[name_channels_list.index(arg)].id
            if not discord_id:
                await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                     f"This argument ({arg}) is not a valid id, please try again", 30)
                valid = False

        return valid, discord_id

    @staticmethod
    async def valid_arg(self, ctx, arg, server_id=None):
        name_channels_list = []
        discord_id = None
        valid, discord_id, obj_type = await self.valid_person(self, ctx, arg, discord_id)

        if not valid and arg.isdigit():
            valid = self.client.get_guild(int(arg))
            obj_type = "Server"

        if not valid:
            valid, discord_id = await self.valid_channel(self, ctx, arg, server_id, discord_id)
            obj_type = "Channel"
        if str(discord_id) not in arg and name_channels_list and arg not in name_channels_list:
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 f"This format is wrong, please use **{config.prefix}help**", 30)
            valid = False
            obj_type = "None"

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
        await ctx.send(embed=embed, delete_after=delete)

    @staticmethod
    def add_song(path, r):
        with open(path, 'wb') as f:
            for chunk in r.iter_content():
                if chunk:
                    f.write(chunk)
        f.close()
