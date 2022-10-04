import logging

import config
import re
from resources.audio.models import Audio, AudioInEntity, AudioInServer
from resources.server.models import Server
from resources.entity.models import Entity
import asyncio
import discord
from asgiref.sync import sync_to_async


class Helpers:

    @staticmethod
    async def get_or_create_object(obj, kwargs):
        return await sync_to_async(obj.objects.get_or_create, thread_sensitive=True)(**kwargs)

    @staticmethod
    async def filter_object(obj, kwargs):
        return await sync_to_async(obj.objects.filter, thread_sensitive=True)(**kwargs)

    @staticmethod
    async def get_object(obj, kwargs):
        return await sync_to_async(obj.objects.get, thread_sensitive=True)(**kwargs)

    @staticmethod
    async def get_random_object(obj):
        return await sync_to_async(obj.objects.order_by('?').first(), thread_sensitive=True)()

    @staticmethod
    async def get_async_audio(async_obj, kwargs):
        async for obj in async_obj.objects.filter(**kwargs):
            obj_audio = await obj.audios.order_by('?').afirst()
            return await sync_to_async(lambda: obj_audio.audio)()

    @staticmethod
    async def get_async_audio_list(async_obj, kwargs):
        audio_name_list = []
        audio_hashcode_list = []
        async for obj in async_obj.objects.filter(**kwargs):
            audio_name_list.append(obj.name)
            hashcode = await sync_to_async(lambda: obj.audio.hashcode)()
            audio_hashcode_list.append(hashcode)
        return audio_name_list, audio_hashcode_list

    @staticmethod
    async def required_role(self, ctx):
        has_role = True
        if "FM" not in (roles.name for roles in ctx.message.author.roles):
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 f"You need _**FM**_ role to use this command.\n"
                                 "Only members who have administrator permissions are able to assign _**FM**_ role.\n"
                                 f"Command: \"**{config.prefix} role @mention**\"")
            has_role = False

        return has_role

    @staticmethod
    async def insert_file_db(self, ctx, arg: str, filename: str, hashcode: str):

        audio, _ = await self.get_or_create_object(Audio, {'hashcode': hashcode})
        server, _ = await self.get_or_create_object(Server, {'discord_id': ctx.message.guild.id})

        if arg is None:
            audio, created = await self.get_or_create_object(AudioInServer,
                                                             {'audio': audio, 'server': server, 'name': filename})
        else:
            discord_id = int(re.findall(r'\b\d+\b', arg)[0])
            entity, _ = await self.get_or_create_object(Entity, {'discord_id': discord_id, 'server': server})
            audio, created = await self.get_or_create_object(AudioInEntity,
                                                             {'audio': audio, 'entity': entity, 'name': filename})

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
