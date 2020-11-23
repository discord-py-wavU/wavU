import discord
from discord.ext import commands

client = commands.Bot(command_prefix='=')

@client.command(name='puto')
async def version(context):
    await context.message.channel.send('el que lee')


@client.event
async def on_ready():
    general_channel = client.get_channel(780505808961273884)
    await general_channel.send('hi')


client.run(config.token)
