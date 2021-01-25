import random
import time
from datetime import datetime

import discord
from discord.ext import commands
from discord.utils import get

from os import listdir
from os.path import isfile, join


class VoiceCommands(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        path = '/Users/facub/Documents/GitHub/pepebot/audio'
        if after.channel is not None and before.channel is not member.voice.channel and member != self.client.user:
            try:
                voice = get(self.client.voice_clients, guild=member.guild)
                if voice and voice.is_connected():
                    await voice.move_to(after.channel)
                else:
                    voice = await after.channel.connect()
                onlyfiles = [f for f in listdir(path) if isfile(join(path, f)) and '.mp3' in f]
                #print(get_current_time() + ' => ' + member.guild.name + ' :: '
                #      + member.display_name + ' -> ' + after.channel.name)
                audios_to_play = onlyfiles
                time.sleep(1)
                #print(self.client.voice_clients)
                audio_to_play = 'audio/' + random.choice(audios_to_play)
                voice.play(discord.FFmpegPCMAudio(audio_to_play))
                while voice.is_playing():
                    time.sleep(0.3)
                voice.stop()
                if voice.is_connected():
                    print(voice.latency)
                    # while voice.latency == float('inf'):
                    # print(voice.latency)
                    # print(voice.average_latency)
                    await voice.disconnect()

                if after.channel.name == 'General' or after.channel.name == 'aaaaa':
                    print('User is in channel')
                    print(member.voice)
                    #print(member.voice_clients)
                    #await member.disconnect()

                    # await member.voice.disconnect()
                    # voice2 = get(member.voice.channel, guild=member.guild)
                    # print(voice2)
                    # await voice.disconnect()

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
