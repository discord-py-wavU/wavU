# -*- coding: utf-8 -*-

from discord.ext import commands

from resources.bot.command_base import CommandBase


class ListCommand(commands.Cog, CommandBase):

    def __init__(self, client):
        super().__init__()
        self.client = client

    @commands.command(name='list', aliases=['show', 'List', 'Show'])
    async def show_list(self, ctx, arg=None):

        if not await self.role_required(ctx):
            return

        _, audios, _ = await self.get_audios(ctx, arg)

        if audios:
            list_songs = ""
            for index, song in enumerate(audios):
                list_songs = list_songs + f"{str(index + 1)}. {song}\n"
            list_songs = f"{list_songs}"
            await self.embed_msg(ctx, f"List .mp3 files:", f"{list_songs}", 30)
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}", "_List is empty_")


async def setup(client):
    await client.add_cog(ListCommand(client))
