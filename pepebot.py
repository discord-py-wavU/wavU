import discord

client = discord.Client()

@client.event
async def on_ready():
    general_channel = client.get_channel(780505808961273884)

    await general_channel.send('hi')


client.run('Mzc5MTU4Nzc0MTU5NTA3NDU5.WgftIA.n-WrY7dg3ZvJzfVcE-IKldH-Hww')