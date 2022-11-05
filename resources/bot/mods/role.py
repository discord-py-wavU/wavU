# -*- coding: utf-8 -*-

from discord.utils import get
from discord.ext import commands
from resources.bot.helpers import Helpers


class RoleCommand(commands.Cog, Helpers):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['Role'])
    async def role(self, ctx, arg=None):
        roles = get(ctx.guild.roles, name="FM")

        if ctx.message.author.guild_permissions.administrator:
            if arg is None or not ctx.message.mentions:
                await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                          f"You need to mention who you want to give _**FM**_ role")
            else:
                if "FM" in (roles.name for roles in ctx.message.mentions[0].roles):
                    await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                              f"This person already has _**FM**_ role")
                else:
                    await ctx.message.mentions[0].add_roles(roles)
                    await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                              f"_**{str(ctx.message.mentions[0])}**_ has _File Manager_ role")
        else:
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                      f"You need to have administrator permissions to assign FM role")


def setup(client):
    client.add_cog(RoleCommand(client))
