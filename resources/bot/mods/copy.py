# -*- coding: utf-8 -*-

import asyncio
import logging

import discord
from discord.ext import commands

import config
from resources.audio.models import Audio, AudioInServer, AudioInEntity
from resources.bot.helpers import Helpers, running_commands
from resources.entity.models import Entity
from resources.server.models import Server


class CopyCommand(commands.Cog, Helpers):

    def __init__(self, client):
        super().__init__()
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

        loop = self.client.loop or asyncio.get_event_loop()

        if audios:
            actual_page = 0

            self.list_audios = [audios[i:i + 10] for i in range(0, len(audios), 10)]
            self.page_len = len(self.list_audios)

            msg = "Choose a _number_ to move a _**.mp3**_ file\n"
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
                        try:
                            offset = (self.actual_page * 10) + int(self.dict_numbers[str(reaction.emoji)]) - 1
                            audio = audios[offset]
                            hashcode = hashcodes[offset]
                            valid = await self.copy_file(self, ctx, audio, hashcode, discord_id_dest, server_id,
                                                        obj_type_dest)
                            if valid:
                                await self.embed_msg(ctx, f"{ctx.message.author.name} here is your file",
                                                    f'**{audios[offset]}** has been _**moved**_', 30)
                        except IndexError as IE:
                            logging.warning(IE)
                    elif str(reaction.emoji) == '❌':
                        await emb_msg.delete()
                        embed = discord.Embed(title=f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                              color=0xFC65E1)
                        await ctx.send(embed=embed, delete_after=10)
                        running_commands.remove(ctx.author)
                        return

            except asyncio.TimeoutError:
                await self.embed_msg(ctx, f"Timeout!",
                                     'This command was cancelled', 10)
                await emb_msg.delete()
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                 'List is empty')
        running_commands.remove(ctx.author)


async def setup(client):
    await client.add_cog(CopyCommand(client))
