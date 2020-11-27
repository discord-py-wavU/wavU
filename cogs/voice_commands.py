import time
from datetime import datetime

import discord
from discord.ext import commands
from discord.utils import get

import audio.song_list


class VoiceCommands(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel is not None and before.channel is not member.voice.channel and member != self.client.user:
            try:
                voice = get(self.client.voice_clients, guild=member.guild)
                if voice and voice.is_connected():
                    await voice.move_to(after.channel)
                else:
                    voice = await after.channel.connect()
                print(get_current_time() + ' => ' + member.guild.name + ' :: '
                      + member.display_name + ' -> ' + after.channel.name)
                time.sleep(0.6)
                voice.play(discord.FFmpegPCMAudio(audio.song_list.ctm))
                time.sleep(1.7)
                await voice.disconnect()
            except discord.ClientException:
                print("Error")
        elif after.channel is None and len(before.channel.members) == 1:
            voice = get(self.client.voice_clients)
            if voice and voice.is_connected():
                await voice.disconnect()

    @commands.command()
    async def time(self, ctx):
        print(get_current_time())


def get_current_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time


def setup(client):
    client.add_cog(VoiceCommands(client))
