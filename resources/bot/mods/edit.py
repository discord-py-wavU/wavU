# -*- coding: utf-8 -*-

import asyncio

import discord
from asgiref.sync import sync_to_async
from discord.ext import commands

from resources.bot.helpers import Helpers, running_commands


class EditCommand(commands.Cog, Helpers):

    def __init__(self, client):
        super().__init__()
        self.client = client

    @staticmethod
    async def edit_obj_and_file(obj, hashcode, name):
        obj_filtered = await sync_to_async(obj.filter, thread_sensitive=True)(audio__hashcode=hashcode)
        await sync_to_async(obj_filtered.update, thread_sensitive=True)(name=name)

    @staticmethod
    async def get_name(self, ctx):
        def check_name(m):
            return (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                   or str(m.content).lower() == "cancel"

        await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                             "Choose a new _name_ or type _**cancel**_ to not edit", 5)

        msg_edit = await self.client.wait_for('message', check=check_name, timeout=60)

        return msg_edit

    @commands.command(aliases=['Edit'])
    async def edit(self, ctx, arg=None):

        if not await self.check_if_running(self, ctx):
            return

        has_role = await self.required_role(self, ctx)
        if not has_role:
            return

        valid, discord_id, obj_type = await self.valid_arg(self, ctx, arg)
        if not valid:
            return

        obj, audios, hashcodes = await self.search_songs(self, ctx, arg)

        loop = self.client.loop or asyncio.get_event_loop()

        if audios:
            actual_page = 0

            self.list_audios = [audios[i:i + 10] for i in range(0, len(audios), 10)]
            self.page_len = len(self.list_audios)

            msg = "Choose a _number_ to edit a file _name_\n"
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
                        msg_name = await self.get_name(self, ctx)
                        offset = (self.actual_page * 10) + int(self.dict_numbers[str(reaction.emoji)]) - 1
                        hashcode = hashcodes[offset]
                        await self.edit_obj_and_file(obj, hashcode, msg_name.content)
                        audios[offset] = msg_name.content + ".mp3"
                        self.list_audios = [audios[i:i + 10] for i in range(0, len(audios), 10)]
                        await self.edit_message(self, emb_msg, msg)
                        await msg_name.delete()
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
    await client.add_cog(EditCommand(client))
