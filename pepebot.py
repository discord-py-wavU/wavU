import discord
from config import *
from discord.ext import commands

client = commands.Bot(command_prefix='=')

@client.command(name='puto')
async def version(context):
    await context.message.channel.send('el que lee')

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game('Minecraft'))

@client.event
async def on_message(message):
    if message.content == 'eh vo':
        await message.author.send('que te pasa gil?')

    await client.process_commands(message)

client.run(token)

