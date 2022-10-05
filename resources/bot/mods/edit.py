import asyncio
import os

from asgiref.sync import sync_to_async

import config
from resources.bot.helpers import Helpers
from discord.ext import commands


class EditCommand(commands.Cog, Helpers):

    def __init__(self, client):
        self.client = client

    @staticmethod
    async def edit_obj_and_file(obj, hashcode, name):
        obj_filtered = await sync_to_async(obj.filter, thread_sensitive=True)(audio__hashcode=hashcode)
        await sync_to_async(obj_filtered.update, thread_sensitive=True)(name=name)

    @commands.command(aliases=['Edit'])
    async def edit(self, ctx, arg=None):

        has_role = await self.required_role(self, ctx)
        if not has_role:
            return

        obj, audios, hashcodes = await self.search_songs(self, ctx, arg)

        if audios:
            msg = "Choose a _number_ to edit a _**.mp3**_ file _name_"

            await self.show_audio_list(self, ctx, audios, msg)

            def check_number(m):
                return (m.content.isdigit() and
                        m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                       or str(m.content).lower() == "cancel" \
                       or str(m.content).lower() == "all"

            def check_name(m):
                return (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                       or str(m.content).lower() == "cancel"

            try:
                for i in range(3):

                    msg = await self.client.wait_for('message', check=check_number, timeout=30)

                    if msg.content.isdigit() and int(msg.content) <= len(audios) and int(msg.content) != 0:
                        await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                             "Choose a new _name_ or type _**cancel**_ to not edit", 30)
                        msg_edit = await self.client.wait_for('message', check=check_name, timeout=60)

                        if str(msg_edit.content).lower() == "cancel":
                            await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                                 "Nothing has been _**edited**_", 30)
                        else:
                            hashcode = hashcodes[int(msg.content) - 1]
                            name = msg_edit.content
                            await self.edit_obj_and_file(obj, hashcode, name)
                            await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                                 f'** has been edited to ** {msg_edit.content}.mp3**', 30)
                        break
                    elif str(msg.content).lower() == "cancel":
                        await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                             "Nothing has been _**edited**_", 30)
                        break
                    elif int(msg.content) > len(audios) or int(msg.content) == 0:
                        await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                             "That number is not an option. Try again **(" + str(i + 1) + "/3)**", 10)
                        if i == 2:
                            await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                                 "None of the attempts were correct, _**edit**_ has been aborted",
                                                 10)
            except asyncio.TimeoutError:
                await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:", "Time is up!", 15)
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}", "_List is empty_", 10)


def setup(client):
    client.add_cog(EditCommand(client))
