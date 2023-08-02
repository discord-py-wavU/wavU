# -*- coding: utf-8 -*-

import asyncio
import logging

import discord
from asgiref.sync import sync_to_async
from discord.ext import commands

from resources.bot.helpers import Message, Button, Status, Checker, RUNNING_COMMAND


class OffCommand(commands.Cog, Message, Button, Status, Checker):

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
            RUNNING_COMMAND.remove(ctx.author)
            return

        valid, discord_id, obj_type = await self.valid_arg(ctx, arg)
        if not valid:
            RUNNING_COMMAND.remove(ctx.author)
            return
        
        objects, audios, hashcodes = await self.get_audios(ctx, arg)

        tuple_obj = [[obj.name, obj.enabled] for obj in objects]

        if audios:
            self.actual_page = 0
            self.list_audios = [tuple_obj[i:i + 10] for i in range(0, len(tuple_obj), 10)]
            self.page_len = len(self.list_audios)

            msg = "Choose a number to disabled a file\n"
            self.view = discord.ui.View()
            await self.button_interactions()
            await self.show_status_list(ctx, self.list_audios[0])

            def check(user):
                return user != self.client.user and user.guild.id == ctx.guild.id

            try:
                while True:
                    btn = await self.client.wait_for('interaction', check=check, timeout=600)
                    custom_id = btn.data.get('custom_id')
                    if custom_id.isdigit():
                        self.interaction = int(custom_id)
                    else:
                        self.interaction = custom_id

                    if self.interaction == "right" or self.interaction == "left":
                        await self.interaction_button_status(msg)
                        await btn.response.defer()

                    if isinstance(self.interaction, int):
                        try:
                            offset = (self.actual_page * 10) + self.interaction - 1
                            hashcode = hashcodes[offset]
                            await self.disable_audio(objects, hashcode)
                            await self.embed_msg_with_interaction(btn, f"{ctx.message.author.name}:",
                                                 f'**{audios[offset]}** has been _**disabled**_', 5)
                            tuple_obj[offset][1] = False
                            self.list_audios = [tuple_obj[i:i + 10] for i in range(0, len(tuple_obj), 10)]
                            await self.edit_status_message(msg)
                        except IndexError as IE:
                            logging.warning(IE)
                    elif self.interaction == 'cancel':
                        await btn.response.defer()
                        await self.emb_msg.delete()
                        embed = discord.Embed(title=f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                              color=0xFC65E1)
                        await ctx.send(embed=embed, delete_after=10)
                        RUNNING_COMMAND.remove(ctx.author)
                        return

            except asyncio.TimeoutError:
                await self.embed_msg(ctx, f"Timeout!",
                                     'This command was cancelled', 10)
                await self.emb_msg.delete()
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                 'List is empty')
        RUNNING_COMMAND.remove(ctx.author)


async def setup(client):
    await client.add_cog(OffCommand(client))
