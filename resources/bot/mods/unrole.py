# -*- coding: utf-8 -*-

from discord.ext import commands
from discord.utils import get

from resources.bot.command_base import CommandBase


class UnroleCommand(commands.Cog, CommandBase):

    def __init__(self, client):
        super().__init__()
        self.client = client

    @commands.command(aliases=['Unrole'])
    async def unrole(self, ctx, arg=None):

        fm_rol = get(ctx.guild.roles, name="FM")
        username = ctx.message.author.name.capitalize()
        name_msg = f"Hey {username}"

        if ctx.message.author.guild_permissions.administrator:
            if arg is None or not ctx.message.mentions:
                name_msg = f"Hey {username}"
                value_msg = f"You need to mention who you want to remove _**FM**_ role"
                await self.embed_msg(ctx, name_msg, value_msg)
            else:
                if "FM" in (roles.name for roles in ctx.message.mentions[0].roles):
                    await ctx.message.mentions[0].remove_roles(fm_rol)
                    value_msg = f"You have removed _**{str(ctx.message.mentions[0])}**_ from _File Manager_ role"
                    await self.embed_msg(ctx, name_msg, value_msg)
                else:
                    value_msg = f"This person hasn't FM role"
                    await self.embed_msg(ctx, name_msg, value_msg)
        else:
            name_msg = f"I'm sorry {username} :cry:"
            value_msg = f"You need to have administrator permissions to assign FM role"
            await self.embed_msg(ctx, name_msg, value_msg)


async def setup(client):
    await client.add_cog(UnroleCommand(client))
