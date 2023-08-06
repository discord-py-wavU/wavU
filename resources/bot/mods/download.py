# Stantard imports
import asyncio
import logging
# Discord imports
import discord
from discord.ext import commands
# Own imports
import config
# Project imports
from resources.bot.command_base import CommandBase, RUNNING_COMMAND


class DownloadCommand(commands.Cog, CommandBase):

    def __init__(self, client):
        super().__init__()
        self.client = client

    @commands.command(aliases=['Download', 'dl', 'Dl', 'DL'])
    async def download(self, ctx, arg=None):

        if not await self.user_input_valid(ctx, arg):
            return

        objects, audios, hashcodes = await self.get_audios(ctx, arg)

        if audios:
            self.actual_page = 0

            self.list_audios = [audios[i:i + 10]
                                for i in range(0, len(audios), 10)]
            self.page_len = len(self.list_audios)

            self.view = discord.ui.View()
            self.instruction_msg = f"Choose a _number_ to change the file volume\n"
            await self.button_interactions()
            await self.show_audio_list(ctx)

            def check(user):
                return user != self.client.user and user.guild.id == ctx.guild.id

            try:
                while True:
                    btn = await self.client.wait_for('interaction', check=check, timeout=600)
                    await self.get_interaction(btn)

                    if self.interaction == 'right' or self.interaction == 'left':
                        await self.move_page(btn)

                    if isinstance(self.interaction, int):
                        try:
                            offset = (self.actual_page * 10) + \
                                self.interaction - 1
                            await btn.response.send_message(
                                file=discord.File(fp=f"{config.path}/{hashcodes[offset]}.mp3",
                                                  filename=f"{audios[offset]}.mp3"),
                                delete_after=5
                            )
                        except IndexError as IE:
                            logging.warning(IE)
                    elif self.interaction == 'cancel':
                        await btn.response.defer()
                        await self.emb_msg.delete()
                        embed = discord.Embed(title=f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                              color=0xFC65E1)
                        await ctx.send(embed=embed, delete_after=10)
                        RUNNING_COMMAND.remove(ctx.author)
                        return

            except asyncio.TimeoutError:
                await self.embed_msg(ctx, f"Timeout!",
                                     'This command was cancelled', 10)
                await self.emb_msg.delete()
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                 'List is empty')
        RUNNING_COMMAND.remove(ctx.author)


async def setup(client):
    await client.add_cog(DownloadCommand(client))
