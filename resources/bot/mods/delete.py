# -*- coding: utf-8 -*-

import asyncio
import logging
import os

import discord
from asgiref.sync import sync_to_async
from discord.ext import commands

import config
from resources.bot.helpers import Helpers, RUNNING_COMMAND


class DeleteCommand(commands.Cog, Helpers):

    def __init__(self, client):
        super().__init__()
        self.client = client

    def deleted_object(self, obj, hashcode):
        obj_filtered = obj.filter(audio__hashcode=hashcode)
        obj_filtered.delete()

    @staticmethod
    async def delete_obj_and_file(self, obj, hashcode):
        try:
            os.remove(f"{config.path}/{hashcode}.mp3")
        except FileNotFoundError as FNFE:
            logging.warning(FNFE)
        finally:
            await sync_to_async(self.deleted_object, thread_sensitive=True)(obj, hashcode)

    @commands.command(aliases=['Delete', 'del', 'Del', 'remove', 'Remove', 'rm', 'Rm', 'RM'])
    async def delete(self, ctx, arg=None):

        if not await self.check_if_running(self, ctx):
            return

        has_role = await self.required_role(self, ctx)
        if not has_role:
            RUNNING_COMMAND.remove(ctx.author)
            return

        valid, discord_id, obj_type = await self.valid_arg(self, ctx, arg)
        if not valid:
            RUNNING_COMMAND.remove(ctx.author)
            return

        obj, audios, hashcodes = await self.search_songs(self, ctx, arg)

        loop = self.client.loop or asyncio.get_event_loop()

        if audios:
            actual_page = 0
            self.actual_page = 0

            self.list_audios = [audios[i:i + 10] for i in range(0, len(audios), 10)]
            self.page_len = len(self.list_audios)

            msg = f"Choose a number to delete a file\n"
            emb_msg = await self.show_audio_list(self, ctx, self.list_audios[0], msg)

            def check(reaction, user):
                return user != self.client.user and user.guild.id == ctx.guild.id

            task_core_reaction = loop.create_task(self.core_reactions(self, emb_msg, actual_page))

            try:
                while True:
                    reaction, user = await self.client.wait_for('reaction_add', check=check, timeout=600)

                    if reaction:
                        if actual_page:
                            await actual_page
                        if task_core_reaction is not None:
                            await task_core_reaction
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

                    if str(reaction.emoji) in CHOOSE_NUMBER:
                        if actual_page:
                            await actual_page
                        if task_core_reaction is not None:
                            await task_core_reaction
                        try:
                            offset = (self.actual_page * 10) + int(CHOOSE_NUMBER[str(reaction.emoji)]) - 1
                            await self.delete_obj_and_file(self, obj, hashcodes[offset])
                            audios.remove(audios[offset])
                            prev_len = len(self.list_audios[self.actual_page])
                            self.list_audios = [audios[i:i + 10] for i in range(0, len(audios), 10)]
                            actual_len = len(self.list_audios[self.actual_page])
                            self.page_len = len(self.list_audios)
                        except IndexError as IE:
                            logging.warning(IE)
                            if self.actual_page:
                                if not self.list_audios[self.actual_page]:
                                    self.actual_page -= 1
                                    self.page_len -= 1
                                    actual_page = loop.create_task(
                                        self.arrows_reactions(self, emb_msg, reaction, msg, True))
                                    for ind in range(10):
                                        await asyncio.sleep(0.1)
                                        await emb_msg.add_reaction(CHOOSE_NUMBER[str(ind + 1)])
                                continue
                            else:
                                await emb_msg.delete()
                                embed = discord.Embed(title=f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                                      color=0xFC65E1)
                                await ctx.send(embed=embed, delete_after=10)
                                RUNNING_COMMAND.remove(ctx.author)
                                return
                        if prev_len > actual_len:
                            await emb_msg.remove_reaction(emoji=CHOOSE_NUMBER[str(actual_len + 1)],
                                                          member=self.client.user)

                        msg = f"Choose a number to delete a file\n"
                        await self.edit_message(self, emb_msg, msg)
                    elif str(reaction.emoji) == '❌':
                        await emb_msg.delete()
                        embed = discord.Embed(title=f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                              color=0xFC65E1)
                        await ctx.send(embed=embed, delete_after=10)
                        RUNNING_COMMAND.remove(ctx.author)
                        return

            except asyncio.TimeoutError:
                await self.embed_msg(ctx, f"Timeout!",
                                     'This command was cancelled', 10)
                await emb_msg.delete()
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                 'List is empty')
        RUNNING_COMMAND.remove(ctx.author)


async def setup(client):
    await client.add_cog(DeleteCommand(client))
