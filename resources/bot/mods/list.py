# -*- coding: utf-8 -*-

from discord.ext import commands

from resources.bot.helpers import Helpers


class ListCommand(commands.Cog, Helpers):

    def __init__(self, client):
        self.client = client

    @commands.command(name='list', aliases=['show', 'List', 'Show'])
    async def show_list(self, ctx, arg=None):

        has_role = await self.required_role(self, ctx)
        if not has_role:
            return

        valid, discord_id, obj_type = await self.valid_arg(self, ctx, arg)
        if not valid:
            return

        obj, audios, hashcodes = await self.search_songs(self, ctx, arg)

        if audios:
            list_songs = ""
            for index, song in enumerate(audios):
                list_songs = list_songs + f"{str(index + 1)}. {song.split('.mp3')[0]}\n"
            list_songs = f"{list_songs}"
            await self.embed_msg(ctx, f"List .mp3 files:", f"{list_songs}", 30)
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}", "_List is empty_")


def setup(client):
    client.add_cog(ListCommand(client))
