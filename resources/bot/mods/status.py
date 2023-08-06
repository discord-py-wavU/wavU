# -*- coding: utf-8 -*-

from discord.ext import commands

from resources.bot.command_base import CommandBase


class Status(commands.Cog, CommandBase):

    def __init__(self, client):
        super().__init__()
        self.client = client

    @commands.command()
    async def status(self, ctx, arg=None):

        server_id = ctx.message.guild.id

        valid = await self.valid_arg(ctx, arg)
        if not valid:
            return

        objects, _, _ = await self.get_audios(ctx, arg)

        if self.obj_type == "Server" and server_id != self.discord_id:
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


async def setup(client):
    await client.add_cog(Status(client))
