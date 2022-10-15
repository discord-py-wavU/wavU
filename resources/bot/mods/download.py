import asyncio

import discord
from discord.ext import commands

import config
from resources.bot.helpers import Helpers


class DownloadCommand(commands.Cog, Helpers):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['Download', 'dl', 'Dl', 'DL'])
    async def download(self, ctx, arg=None):

        has_role = await self.required_role(self, ctx)
        if not has_role:
            return

        valid, discord_id, obj_type = await self.valid_arg(self, ctx, arg)
        if not valid:
            return

        obj, audios, hashcodes = await self.search_songs(self, ctx, arg)

        if audios:

            msg = "Choose a _number_ to download a _**.mp3**_ file\n"

            await self.show_audio_list(self, ctx, audios, msg)

            def check(m):
                return (m.content.isdigit() and
                        m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                       or str(m.content).lower() == "cancel" \
                       or str(m.content).lower() == "all"

            try:
                for i in range(3):

                    msg = await self.client.wait_for('message', check=check, timeout=30)
                    if msg.content.isdigit() and int(msg.content) <= len(audios) and int(msg.content) != 0:
                        hashcode = hashcodes[int(msg.content) - 1]
                        await ctx.send(file=discord.File(fp=f"{config.path}/{hashcode}.mp3",
                                                         filename=f"{audios[int(msg.content) - 1]}.mp3"))
                        await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                             f'**{audios[int(msg.content) - 1]}** has been _**downloaded**_', 30)
                        break

                    elif msg.content == "cancel" or msg.content == "Cancel":
                        await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                             "Nothing has been _**downloaded**_", 30)
                        break
                    elif int(msg.content) > len(audios) or int(msg.content) == 0:
                        await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                             "That number is not an option. Try again **(" + str(i + 1) + "/3)**", 10)
                        if i == 2:
                            await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                                 "None of the attempts were correct, _**delete**_ has been aborted",
                                                 10)
            except asyncio.TimeoutError:
                await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:", "Time is up!", 15)
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}", "_List is empty_", 10)


def setup(client):
    client.add_cog(DownloadCommand(client))
