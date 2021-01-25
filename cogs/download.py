import discord
from discord.ext import commands
import os
import requests

class DownloadFile(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.attachments:
            headers = {
            'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
            }

            r = requests.get(message.attachments[0].url, headers=headers, stream=True)
            mp3 = message.attachments[0].filename.split('.')
            if mp3[len(mp3)-1] == "mp3":
                with open('audio/' + message.attachments[0].filename, 'wb') as f:
                    for chunk in r.iter_content():
                        if chunk:
                            f.write(chunk)
                f.close()




def setup(client):
    client.add_cog(DownloadFile(client))