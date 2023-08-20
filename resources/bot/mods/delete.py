# Standard imports
import asyncio
import logging
import os
# Extras imports
from asgiref.sync import sync_to_async
# Discord imports
import discord
from discord.ext import commands
# Own imports
import config
import content
# Project imports
from resources.bot.command_base import CommandBase, RUNNING_COMMAND


class DeleteCommand(commands.Cog, CommandBase):

    def __init__(self, client):
        super().__init__()
        self.client = client

    def deleted_object(self, obj, hashcode):
        obj_filtered = obj.filter(audio__hashcode=hashcode)
        obj_filtered.delete()

    async def delete_obj_and_file(self, obj, hashcode):
        try:
            os.remove(f"{config.path}/{hashcode}.mp3")
        except FileNotFoundError as FNFE:
            logging.warning(FNFE)
        finally:
            await sync_to_async(self.deleted_object, thread_sensitive=True)(obj, hashcode)

    @commands.command(aliases=['Delete', 'del', 'Del', 'remove', 'Remove', 'rm', 'Rm', 'RM'])
    async def delete(self, ctx, arg=None):

        if not await self.user_input_valid(ctx, arg):
            return

        objects, audios, hashcodes = await self.get_audios(ctx, arg)

        if audios:
            self.actual_page = 0

            self.list_audios = [audios[i:i + 10] for i in range(0, len(audios), 10)]
            self.page_len = len(self.list_audios)

            self.view = discord.ui.View()
            self.instruction_msg = f"Choose a _number_ to delete \n"
            await self.button_interactions()
            await self.show_audio_list(ctx)

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
                            await self.delete_obj_and_file(objects, hashcodes[offset])
                            audios.remove(audios[offset])
                            old_len = len(self.list_audios)
                            self.list_audios = [audios[i:i + 10] for i in range(0, len(audios), 10)]
                            is_first_page = self.actual_page == self.page_len - 1
                            if self.list_audios and len(self.list_audios) + 1 == old_len and is_first_page:
                                self.actual_page -= 1
                                self.page_len -= 1
                            elif not self.list_audios:
                                await btn.response.defer()
                                await self.emb_msg.delete()
                                await self.add_special_buttons(ctx)
                                RUNNING_COMMAND.remove(ctx.author)
                                return

                            self.view.clear_items()
                            await self.button_interactions()
                            await self.edit_message(ctx)
                            await btn.response.defer()
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
            username = ctx.message.author.name.capitalize()
            await self.embed_msg(ctx, content.hey_msg.format(username), content.empty_list)
        RUNNING_COMMAND.remove(ctx.author)


async def setup(client):
    await client.add_cog(DeleteCommand(client))
