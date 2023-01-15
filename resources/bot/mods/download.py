# -*- coding: utf-8 -*-

import asyncio
import logging

import discord
from discord.ext import commands

import config
from resources.bot.helpers import Helpers, running_commands


class DownloadCommand(commands.Cog, Helpers):

    def __init__(self, client):
        super().__init__()
        self.client = client

    @commands.command(aliases=['Download', 'dl', 'Dl', 'DL'])
    async def download(self, ctx, arg=None):

        if not await self.check_if_running(self, ctx):
            return

        loop = self.client.loop or asyncio.get_event_loop()

        has_role = await self.required_role(self, ctx)
        if not has_role:
            running_commands.remove(ctx.author)
            return

        valid, discord_id, obj_type = await self.valid_arg(self, ctx, arg)
        if not valid:
            running_commands.remove(ctx.author)
            return

        obj, audios, hashcodes = await self.search_songs(self, ctx, arg)

        if audios:
            actual_page = 0

            self.list_audios = [audios[i:i + 10] for i in range(0, len(audios), 10)]
            self.page_len = len(self.list_audios)

            msg = f"Choose a number to download a file\n"
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
                            await ctx.send(file=discord.File(fp=f"{config.path}/{hashcodes[offset]}.mp3",
                                                             filename=f"{audios[offset]}.mp3"), delete_after=5)
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
    await client.add_cog(DownloadCommand(client))
