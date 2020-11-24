import discord
from discord.utils import get
from discord.ext import commands
import youtube_dl
import os
from config import token

client = commands.Bot(command_prefix='=')

#events

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game('AAAAAAAAAA'))

@client.event
async def on_message(message):
    if message.content == 'eh vo':
        await message.author.send('que te pasa gil?')

    await client.process_commands(message)

#commands

@client.command(name='puto')
async def version(ctx):
    await ctx.message.channel.send('el que lee')

@client.command()
async def Ping(ctx):
    await ctx.send(f'Pong! {round(client.latency*1000)}ms')


@client.command(pass_content=True)
async def join(ctx):
    try:
        channel = ctx.message.author.voice.channel
        voice = get(client.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()
    except:
        await ctx.send("You are not connected to a voice channel")

@client.command(pass_contex=True)
async def leave(ctx):
    await ctx.voice_client.disconnect()


@client.command(pass_content=True)
async def play(ctx, url):

    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Wait for the current playing music end or use the 'stop' command")
        return
    await ctx.send("Getting everything ready, playing audio soon")
    print("Someone wants to play music let me get that ready for them...")
    voice = get(client.voice_clients, guild=ctx.guild)
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, 'song.mp3')
    voice.play(discord.FFmpegPCMAudio("song.mp3"))
    voice.volume = 100
    voice.is_playing()


client.run(token)

