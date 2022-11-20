# -*- coding: utf-8 -*-

import asyncio

from discord.ext import commands

import config
from resources.audio.models import Audio, AudioInServer, AudioInEntity
from resources.bot.helpers import Helpers
from resources.entity.models import Entity
from resources.server.models import Server


class CopyCommand(commands.Cog, Helpers):

    def __init__(self, client):
        self.client = client

    @staticmethod
    async def copy_file(self, ctx, audio_name, hashcode, discord_id_dest, server_id, obj_type_dest):
        created = False
        server = await self.get_object(self, Server, {'discord_id': server_id})

        if server:
            audio = await self.get_object(self, Audio, {'hashcode': hashcode})
            if obj_type_dest == "Server":
                audio, created = await self.get_or_create_object(
                    AudioInServer, {'audio': audio, 'server': server}, {'name': audio_name})
            elif obj_type_dest == "Channel" or obj_type_dest == "Member":
                entity, created = await self.get_or_create_object(
                    Entity, {'discord_id': discord_id_dest, 'server': server})
                audio, created = await self.get_or_create_object(
                    AudioInEntity, {'audio': audio, 'entity': entity}, {'name': audio_name})

            if not created:
                if discord_id_dest == ctx.message.author.id:
                    await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                         f"You already have this audio, please try again", 30)
                else:
                    await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                         f"You can't copy this audio here, it already exists, please try again", 30)
        else:
            await self.embed_msg(ctx, f"I'm {ctx.message.author.name}",
                                 f"WavU is not joined to server destination, please use {config.prefix}help", 30)

        return created

    @staticmethod
    async def valid_arguments(self, ctx, arg, arg2, arg3):

        valid = True
        discord_id_src = 0
        discord_id_dest = 0
        obj_type_src = None
        obj_type_dest = None

        if arg:
            valid, discord_id_src, obj_type_src = await self.valid_arg(self, ctx, arg)

        if arg3 and valid:
            valid, server_id = await self.valid_server(self, ctx, arg3)
        else:
            server_id = ctx.guild.id
            valid = True

        if arg2 and valid:
            valid, discord_id_dest, obj_type_dest = await self.valid_arg(self, ctx, arg2, server_id)

        if valid:
            guild = self.client.get_guild(int(server_id))
            has_role = await self.required_role(self, ctx, guild)
            if not has_role:
                valid = False

        return valid, discord_id_src, server_id, discord_id_dest, obj_type_dest

    @commands.command(aliases=['Copy', 'co', 'Co', 'share', 'Share', 'sh', 'Sh'])
    async def copy(self, ctx, arg=None, arg2=None, arg3=None):

        has_role = await self.required_role(self, ctx)
        if not has_role:
            return

        if not arg or not arg2:
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 f"This format is wrong, please use **{config.prefix}help**", 30)
            return

        valid, discord_id_src, server_id, discord_id_dest, obj_type_dest = \
            await self.valid_arguments(self, ctx, arg, arg2, arg3)

        if not valid:
            return

        if discord_id_src and discord_id_src == discord_id_dest and server_id == ctx.guild.id:
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 f"You can't copy an audio in the same container", 30)
            return

        if obj_type_dest == "Server" and discord_id_dest and discord_id_dest != server_id:
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 f"You can't copy an audio to _common_ "
                                 f"server files if server destination is different", 30)
            return

        obj, audios, hashcodes = await self.search_songs(self, ctx, arg)

        if audios:

            msg = "Choose a _number_ to move a _**.mp3**_ file\n"

            await self.show_audio_list(self, ctx, audios, msg)

            def check(m):
                return (m.content.isdigit() and
                        m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                       or str(m.content).lower() == "cancel" \
                       or str(m.content).lower() == "all"

            try:
                for i in range(3):

                    msg = await self.client.wait_for('message', check=check, timeout=30)
                    if msg.content.isdigit() and int(msg.content) <= len(audios) and int(msg.content) != 0:
                        audio = audios[int(msg.content) - 1]
                        hashcode = hashcodes[int(msg.content) - 1]
                        valid = await self.copy_file(self, ctx, audio, hashcode, discord_id_dest, server_id,
                                                     obj_type_dest)
                        if valid:
                            await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                                 f'**{audios[int(msg.content) - 1]}** has been _**moved**_', 30)
                        break

                    elif str(msg.content).lower() == "cancel":
                        await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                             "Nothing has been _**moved**_", 30)
                        break
                    elif int(msg.content) > len(audios) or int(msg.content) == 0:
                        await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                             "That number is not an option. Try again **(" + str(i + 1) + "/3)**", 10)
                        if i == 2:
                            await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                                 "None of the attempts were correct, _**moved**_ has been aborted",
                                                 10)
            except asyncio.TimeoutError:
                await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:", "Time is up!", 15)
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}", "_List is empty_", 10)


def setup(client):
    client.add_cog(CopyCommand(client))
