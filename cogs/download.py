import discord
from discord.ext import commands
import os
import requests
import config

class DownloadFile(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def add(self, ctx):

        await ctx.send("Update a .mp3 file")
        
        newpath = config.path + "/" + ctx.message.guild.name
        if not os.path.exists(newpath):
            os.makedirs(newpath)

        def check(m):
            return m.attachments
        msg = await self.client.wait_for('message', check=check)

        headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
        }

        r = requests.get(msg.attachments[0].url, headers=headers, stream=True)
        mp3 = msg.attachments[0].filename.split('.')
        if mp3[len(mp3)-1] == "mp3":
            with open('audio/' + ctx.message.guild.name + '/' + msg.attachments[0].filename, 'wb') as f:
                for chunk in r.iter_content():
                    if chunk:
                        f.write(chunk)
            f.close()
        else:
            await ctx.send("This is not a .mp3 file")

def setup(client):
    client.add_cog(DownloadFile(client))