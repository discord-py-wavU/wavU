from discord.ext import commands


class Random(commands.Cog):

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

    @commands.command()
    async def alan(self, ctx):
        await ctx.message.channel.send('gay')

    @commands.command()
    async def tuvieja(self, ctx):
        await ctx.message.channel.send('entanga')
    
    @commands.command()
    async def pimpumpam(self, ctx):
        await ctx.message.channel.send('como a nisman')
        
    @commands.command()
    async def pepeto(self, ctx):
        await ctx.message.channel.send("Pepeeeto peeepeetooo peeepeetoo", tts=True)


def setup(client):
    client.add_cog(Random(client))



