# -*- coding: utf-8 -*-

import asyncio
import logging

import discord
from asgiref.sync import sync_to_async
from discord.ext import commands

from resources.bot.helpers import Helpers, running_commands


class VolumeCommand(commands.Cog, Helpers):

    def __init__(self, client):
        super().__init__()
        self.client = client

    @staticmethod
    async def set_volume_obj_and_file(obj, volume):
        return await sync_to_async(obj.update, thread_sensitive=True)(volume=volume)

    @staticmethod
    async def get_volume_obj_and_file(obj, hashcode):
        return await sync_to_async(obj.filter, thread_sensitive=True)(audio__hashcode=hashcode)

    @commands.command()
    async def change_volume(self, ctx, audios, offset, obj, hashcode):

        def check_volume(m):
            return (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                   or str(m.content).lower() == "cancel"

        volume_objs = await self.get_volume_obj_and_file(obj, hashcode)
        volume_obj = await volume_objs.afirst()
        await self.embed_msg(ctx, f"This is the current volume: {int(volume_obj.volume)}",
                             "Choose a number **(0-100)** or **cancel**", 10)

        while True:
            msg_volume = await self.client.wait_for('message', check=check_volume, timeout=60)

            if str(msg_volume.content).lower() == "cancel":
                await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                     "_**Volume**_ has not been changed", 5)
                return

            is_valid = True

            if msg_volume.content.count('-') == 1:
                number = msg_volume.content.split('-')[1]
            elif msg_volume.content.count('-') > 1:
                number = 0
                is_valid = False
            else:
                number = msg_volume.content

            if is_valid and number.isdigit():

                if float(0) <= float(msg_volume.content) <= float(100):
                    await self.set_volume_obj_and_file(volume_objs, msg_volume.content)
                    await self.embed_msg(ctx, f"{ctx.message.author.name}:",
                                         f'**{audios[offset]} has been changed to** '
                                         f'**{str(msg_volume.content)}**', 10)
                    await msg_volume.delete()
                    break
                else:
                    await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                         "That **volume** is not valid, try again", 5)
                    await msg_volume.delete()
                    continue
            else:
                await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                     "That is not a number, try again", 5)
                await msg_volume.delete()
                continue

    @commands.command(aliases=['vol', 'Volume', 'Vol'])
    async def volume(self, ctx, arg=None):

        if not await self.check_if_running(self, ctx):
            return

        has_role = await self.required_role(self, ctx)
        if not has_role:
            running_commands.remove(ctx.author)
            return

        valid, discord_id, obj_type = await self.valid_arg(self, ctx, arg)
        if not valid:
            running_commands.remove(ctx.author)
            return

        obj, audios, hashcodes = await self.search_songs(self, ctx, arg)

        loop = self.client.loop or asyncio.get_event_loop()

        if audios:
            actual_page = 0
            self.actual_page = 0

            self.list_audios = [audios[i:i + 10] for i in range(0, len(audios), 10)]
            self.page_len = len(self.list_audios)

            msg = "Choose a _number_ to change the file volume\n"
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
                            hashcode = hashcodes[offset]
                            await self.change_volume(ctx, audios, offset, obj, hashcode)
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
    await client.add_cog(VolumeCommand(client))
