# -*- coding: utf-8 -*-

import asyncio
import logging

import discord
from asgiref.sync import sync_to_async
from discord.ext import commands

from resources.bot.helpers import Helpers, running_commands


class OffCommand(commands.Cog, Helpers):

    def __init__(self, client):
        super().__init__()
        self.client = client

    @staticmethod
    async def disable_audio(obj, hashcode):
        obj_filtered = await sync_to_async(obj.filter, thread_sensitive=True)(audio__hashcode=hashcode)
        await sync_to_async(obj_filtered.update, thread_sensitive=True)(enabled=False)

    @commands.command(alieses=['Off'])
    async def off(self, ctx, arg=None):

        if not await self.check_if_running(self, ctx):
            return

        has_role = await self.required_role(self, ctx)
        if not has_role:
            return

        valid, discord_id, obj_type = await self.valid_arg(self, ctx, arg)
        if not valid:
            return

        objects, audios, hashcodes = await self.search_songs(self, ctx, arg)

        tuple_obj = [[obj.name, obj.enabled] for obj in objects]

        loop = self.client.loop or asyncio.get_event_loop()

        if audios:
            actual_page = 0

            self.list_audios = [tuple_obj[i:i + 10] for i in range(0, len(tuple_obj), 10)]
            self.page_len = len(self.list_audios)

            msg = "Choose a number to disabled a file\n"
            emb_msg = await self.show_status_list(self, ctx, self.list_audios[0])

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

                        actual_page = loop.create_task(self.arrows_reactions(self, emb_msg, reaction, msg, False, True))

                    if str(reaction.emoji) in self.dict_numbers:
                        try:
                            offset = (self.actual_page * 10) + int(self.dict_numbers[str(reaction.emoji)]) - 1
                            hashcode = hashcodes[offset]
                            await self.disable_audio(objects, hashcode)
                            await self.embed_msg(ctx, f"{ctx.message.author.name}:",
                                                f'**{audios[offset]}** has been _**disabled**_', 5)
                            tuple_obj[offset][1] = False
                            self.list_audios = [tuple_obj[i:i + 10] for i in range(0, len(tuple_obj), 10)]
                            await self.edit_status_message(emb_msg, msg, self.list_audios[self.actual_page])
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
    await client.add_cog(OffCommand(client))
