# -*- coding: utf-8 -*-

from discord.ext import commands
from discord.utils import get

from resources.bot.helpers import Helpers


class UnroleCommand(commands.Cog, Helpers):

    def __init__(self, client):
        super().__init__()
        self.client = client

    @commands.command(aliases=['Unrole'])
    async def unrole(self, ctx, arg=None):

        fm_rol = get(ctx.guild.roles, name="FM")

        if ctx.message.author.guild_permissions.administrator:
            if arg is None or not ctx.message.mentions:
                await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                     f"You need to mention who you want to remove _**FM**_ role")
            else:
                if "FM" in (roles.name for roles in ctx.message.mentions[0].roles):
                    await ctx.message.mentions[0].remove_roles(fm_rol)
                    await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                         f"_**{str(ctx.message.mentions[0])}**_ "
                                         f"has been removed from _File Manager_ role")
                else:
                    await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                         f"This person hasn't FM role")
        else:
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 f"You need to have administrator permissions to assign FM role")


async def setup(client):
    await client.add_cog(UnroleCommand(client))
