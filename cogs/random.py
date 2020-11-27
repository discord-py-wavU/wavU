from discord.ext import commands


class _random(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def puto(self, ctx):
        await ctx.message.channel.send('el que lee')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.client.latency * 1000)}ms')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == 'eh vo':
            await message.author.send('que te pasa gil?')
        await self.client.process_commands(message)


def setup(client):
    client.add_cog(_random(client))
