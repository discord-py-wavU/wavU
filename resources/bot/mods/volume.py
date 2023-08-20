# Standard imports
import asyncio
import logging
# Extras imports
from asgiref.sync import sync_to_async
# Discord imports
import discord
from discord.ext import commands
# Own imports
import content
# Project imports
from resources.bot.command_base import CommandBase, RUNNING_COMMAND


class VolumeCommand(commands.Cog, CommandBase):

    def __init__(self, client):
        super().__init__()
        self.client = client

    @staticmethod
    async def set_volume_obj_and_file(obj, volume):
        return await sync_to_async(obj.update, thread_sensitive=True)(volume=volume)

    @staticmethod
    async def get_volume_obj_and_file(obj, hashcode):
        return await sync_to_async(obj.filter, thread_sensitive=True)(audio__hashcode=hashcode)

    async def change_volume(self, ctx, btn, audios, offset, obj, hashcode):

        def check_volume(m):
            return (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                   or str(m.content).lower() == "cancel"

        volume_objs = await self.get_volume_obj_and_file(obj, hashcode)
        volume_obj = await volume_objs.afirst()
        await self.embed_msg_with_interaction(
            btn,
            f"This is the current volume: {int(volume_obj.volume)}",
            "Choose a number **(0-100)** or **cancel**",
            10
        )

        while True:
            msg_volume = await self.client.wait_for('message', check=check_volume, timeout=60)

            if str(msg_volume.content).lower() == "cancel":
                await self.embed_msg(
                    ctx,
                    f"Thanks {ctx.message.author.name} for using wavU :wave:",
                    "_**Volume**_ has not been changed",
                    5
                )
                return

            is_valid = True

            if msg_volume.content.count('-') == 1:
                number = msg_volume.content.split('-')[1]
            elif msg_volume.content.count('-') > 1:
                number = 0
                is_valid = False
            else:
                number = msg_volume.content

            if is_valid and number.isdigit():

                if float(0) <= float(msg_volume.content) <= float(100):
                    await self.set_volume_obj_and_file(volume_objs, msg_volume.content)
                    await self.embed_msg(ctx, f"{ctx.message.author.name.capitalize()}:",
                                         f'**{audios[offset]} has been changed to** '
                                         f'**{str(msg_volume.content)}**', 10)
                    await msg_volume.delete()
                    break
                else:
                    await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                         "That **volume** is not valid, try again", 5)
                    await msg_volume.delete()
                    continue
            else:
                await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                     "That is not a number, try again", 5)
                await msg_volume.delete()
                continue

    @commands.command(aliases=['vol', 'Volume', 'Vol'])
    async def volume(self, ctx, arg=None):

        if not await self.user_input_valid(ctx, arg):
            return

        objects, audios, hashcodes = await self.get_audios(ctx, arg)

        if audios:
            self.actual_page = 0
            self.list_audios = [audios[i:i + 10] for i in range(0, len(audios), 10)]
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
                        await self.move_page(btn, ctx)

                    if isinstance(self.interaction, int):
                        try:
                            offset = (self.actual_page * 10) + self.interaction - 1
                            hashcode = hashcodes[offset]
                            await self.change_volume(ctx, btn, audios, offset, objects, hashcode)
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
        else:
            username = ctx.message.author.name.capitalize()
            await self.embed_msg(ctx, content.hey_msg.format(username), content.empty_list)
        RUNNING_COMMAND.remove(ctx.author)


async def setup(client):
    await client.add_cog(VolumeCommand(client))
