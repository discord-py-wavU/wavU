import discord
from discord.ext import commands

client = commands.Bot(command_prefix='=')

@client.command(name='puto')
async def version(context):
    await context.message.channel.send('el que lee')

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game('Minecraft'))
    general_channel = client.get_channel(780505808961273884)
    await general_channel.send('hi')

@client.event
async def on_message(message):
    if message.content == 'eh vo':
        await message.author.send('que te pasa gil?')

    await client.process_commands(message)

client.run('Mzc5MTU4Nzc0MTU5NTA3NDU5.WgftIA.n-WrY7dg3ZvJzfVcE-IKldH-Hww')

