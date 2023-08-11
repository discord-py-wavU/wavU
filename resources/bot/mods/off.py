# Standard imports
import asyncio
import logging
# Discord imports
import discord
# Extra imports
from asgiref.sync import sync_to_async
# Discord imports
from discord.ext import commands
# Own imports
import content
# Project imports
from resources.bot.command_base import CommandBase, RUNNING_COMMAND


class OffCommand(commands.Cog, CommandBase):

    def __init__(self, client):
        super().__init__()
        self.client = client

    @staticmethod
    async def disable_audio(obj, hashcode):
        obj_filtered = await sync_to_async(obj.filter, thread_sensitive=True)(audio__hashcode=hashcode)
        await sync_to_async(obj_filtered.update, thread_sensitive=True)(enabled=False)

    @commands.command(alieses=['Off'])
    async def off(self, ctx, arg=None):

        if not await self.user_input_valid(ctx, arg):
            return

        objects, audios, hashcodes = await self.get_audios(ctx, arg)

        tuple_obj = [[obj.name, obj.enabled] for obj in objects]

        if audios:
            self.actual_page = 0
            self.list_audios = [tuple_obj[i:i + 10] for i in range(0, len(tuple_obj), 10)]
            self.page_len = len(self.list_audios)

            self.view = discord.ui.View()
            self.instruction_msg = "Choose a number to disabled a file\n"
            await self.button_interactions()
            await self.show_status_list(ctx)

            def check(user):
                return user != self.client.user and user.guild.id == ctx.guild.id

            try:
                while True:
                    btn = await self.client.wait_for('interaction', check=check, timeout=600)
                    await self.get_interaction(btn)

                    if self.interaction == 'right' or self.interaction == 'left':
                        await self.move_page(btn, ctx)

                    if isinstance(self.interaction, int):
                        try:
                            offset = (self.actual_page * 10) + self.interaction - 1
                            hashcode = hashcodes[offset]
                            await self.disable_audio(objects, hashcode)
                            tuple_obj[offset][1] = False
                            self.list_audios = [tuple_obj[i:i + 10] for i in range(0, len(tuple_obj), 10)]
                            await self.edit_message(ctx)
                            await btn.response.defer()
                        except IndexError as IE:
                            logging.warning(IE)
                    elif self.interaction == 'cancel':
                        await btn.response.defer()
                        await self.emb_msg.delete()
                        await self.add_special_buttons(ctx)
                        RUNNING_COMMAND.remove(ctx.author)
                        return

            except asyncio.TimeoutError:
                await self.embed_msg(ctx, f"Timeout!",
                                     'This command was cancelled', 10)
                await self.emb_msg.delete()
            except Exception as e:
                logging.warning(e)
                await self.embed_msg(ctx, f"Error!",
                                     f'Something went wrong: {e}', 10)
                await self.emb_msg.delete()
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}",
                                 'List is empty')
        RUNNING_COMMAND.remove(ctx.author)

    async def add_interaction_buttons(self, ctx):
        prev = self.actual_page
        self.actual_page = await self.choose_direction()

        await self.edit_message(ctx)

        if prev != self.actual_page:
            self.view.clear_items()
            await self.button_interactions()
            await self.emb_msg.edit(view=self.view)

    async def edit_message(self, ctx):
        username = ctx.message.author.name.capitalize()
        hey_msg = content.hey_msg.format(username)
        list_songs = ""
        for index, obj in enumerate(self.list_audios[self.actual_page]):
            emoji = ":white_check_mark:" if obj[1] else ":x:"
            list_songs = list_songs + f"{str(index + 1)}. {obj[0]} {emoji}\n"
        embed = discord.Embed(color=0xFC65E1)
        embed.add_field(name=hey_msg,
                        value=f"{list_songs}",
                        inline=False)
        await self.emb_msg.edit(embed=embed)


async def setup(client):
    await client.add_cog(OffCommand(client))
