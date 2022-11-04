# -*- coding: utf-8 -*-

from discord.ext import commands

from resources.bot.helpers import Helpers


class Status(commands.Cog, Helpers):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def status(self, ctx, arg=None):

        server_id = ctx.message.guild.id

        valid, discord_id, obj_type = await self.valid_arg(self, ctx, arg)
        if not valid:
            return

        objects, audios, hashcodes = await self.search_songs(self, ctx, arg)

        if obj_type == "Server" and server_id != discord_id:
            await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                 "You can't see other server status from here, please another argument", 30)
            return

        list_songs = ""
        for index, obj in enumerate(objects):
            emoji = ":white_check_mark:" if obj.enabled else ":x:"
            list_songs = list_songs + f"{str(index + 1)}. {obj.name} {emoji}\n"
        if list_songs:
            await self.embed_msg(ctx, f"List .mp3 files:", f"{list_songs}")
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}", "_List is empty_", 10)


def setup(client):
    client.add_cog(Status(client))
