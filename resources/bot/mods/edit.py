# Standard imports
import asyncio
import logging
# Extra imports
from asgiref.sync import sync_to_async
# Discord imports
import discord
from discord.ext import commands
# Project imports
from resources.bot.command_base import CommandBase, RUNNING_COMMAND


class EditCommand(commands.Cog, CommandBase):

    def __init__(self, client):
        super().__init__()
        self.client = client

    @staticmethod
    async def edit_obj_and_file(obj, hashcode, name):
        obj_filtered = await sync_to_async(obj.filter, thread_sensitive=True)(audio__hashcode=hashcode)
        await sync_to_async(obj_filtered.update, thread_sensitive=True)(name=name)

    async def get_name(self, btn, ctx):
        def check_name(m):
            return (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                   or str(m.content).lower() == "cancel"

        await self.embed_msg_with_interaction(
            btn,
            f"Hey {ctx.message.author.name}",
            "Choose a new _name_ or type _**cancel**_ to not edit",
            5
        )

        msg_edit = await self.client.wait_for('message', check=check_name, timeout=60)

        return msg_edit

    @commands.command(aliases=['Edit'])
    async def edit(self, ctx, arg=None):

        if not await self.user_input_valid(ctx, arg):
            return

        objects, audios, hashcodes = await self.get_audios(ctx, arg)

        if audios:
            self.actual_page = 0

            self.list_audios = [audios[i:i + 10]
                                for i in range(0, len(audios), 10)]
            self.page_len = len(self.list_audios)

            self.view = discord.ui.View()
            self.instruction_msg = f"Choose a _number_ to edit a file _name_\n"
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
                            msg_name = await self.get_name(btn, ctx)
                            offset = (self.actual_page * 10) + self.interaction - 1
                            hashcode = hashcodes[offset]
                            await self.edit_obj_and_file(objects, hashcode, msg_name.content)
                            audios[offset] = msg_name.content
                            self.list_audios = [audios[i:i + 10] for i in range(0, len(audios), 10)]
                            await self.edit_message(ctx)
                            await msg_name.delete()
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


async def setup(client):
    await client.add_cog(EditCommand(client))
