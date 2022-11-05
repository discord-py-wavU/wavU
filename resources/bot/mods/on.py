# -*- coding: utf-8 -*-

import asyncio

from asgiref.sync import sync_to_async
from discord.ext import commands

from resources.bot.helpers import Helpers


class OnCommand(commands.Cog, Helpers):

    def __init__(self, client):
        self.client = client

    @staticmethod
    async def enable_audio(obj, hashcode):
        obj_filtered = await sync_to_async(obj.filter, thread_sensitive=True)(audio__hashcode=hashcode)
        await sync_to_async(obj_filtered.update, thread_sensitive=True)(enabled=True)

    @commands.command(alieses=['On'])
    async def on(self, ctx, arg=None):

        has_role = await self.required_role(self, ctx)
        if not has_role:
            return

        valid, discord_id, obj_type = await self.valid_arg(self, ctx, arg)
        if not valid:
            return

        obj, audios, hashcodes = await self.search_songs(self, ctx, arg)

        if audios:

            msg = "Choose a number to enabled a _**.mp3**_ file, _**cancel**_ or _**all**_\n"

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
                        hashcode = hashcodes[int(msg.content) - 1]
                        await self.enable_audio(obj, hashcode)
                        await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                             f'**{audios[int(msg.content) - 1]}** has been _**enabled**_', 30)
                        break
                    elif str(msg.content).lower() == "cancel":
                        await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                             "Nothing has been _**enabled**_", 30)
                        break
                    elif str(msg.content).lower() == "all":
                        for index in range(len(audios)):
                            hashcode = hashcodes[index - 1]
                            await self.enable_audio(obj, hashcode)
                        await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                             "All the _**.mp3**_ files has been _**enabled**_", 30)
                        break
                    elif int(msg.content) > len(audios) or int(msg.content) == 0:
                        await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                             "That number is not an option. Try again **(" + str(i + 1) + "/3)**", 10)
                        if i == 2:
                            await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                                 "None of the attempts were correct, _**enabled**_ has been aborted",
                                                 10)

            except asyncio.TimeoutError:
                await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:", "Time is up!", 15)
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}", "_List is empty_", 10)


def setup(client):
    client.add_cog(OnCommand(client))
