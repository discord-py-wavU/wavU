import discord
from discord.ext import commands
from discord.utils import get

class _loggin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def join(self, ctx):
        try:
            channel = ctx.message.author.voice.channel
            voice = get(self.client.voice_clients, guild=ctx.guild)
            if voice and voice.is_connected():
                await voice.move_to(channel)
            else:
                voice = await channel.connect()
        except:
            await ctx.send("You are not connected to a voice channel")

    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()


def setup(client):
    client.add_cog(_loggin(client))