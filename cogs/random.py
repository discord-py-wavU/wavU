import discord
from discord.ext import commands


class _random(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def puto(self, ctx):
        await ctx.message.channel.send('el que lee')

    @commands.command()
    async def Ping(self, ctx):
        await ctx.send(f'Pong! {round(self.client.latency*1000)}ms')

def setup(client):
    client.add_cog(_random(client))