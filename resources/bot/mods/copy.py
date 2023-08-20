# Standard imports
import asyncio
import logging
# Discord imports
import discord
from discord.ext import commands
# Own imports
import config
import content
# Project imports
from resources.audio.models import Audio, AudioInServer, AudioInEntity
from resources.bot.command_base import CommandBase, RUNNING_COMMAND
from resources.entity.models import Entity
from resources.server.models import Server


class CopyCommand(commands.Cog, CommandBase):

    def __init__(self, client):
        super().__init__()
        self.client = client

    async def copy_file(self, ctx, btn, audio_name, hashcode):
        created = False
        server = await self.get_object(Server, {'discord_id': self.server_id})

        if server:
            audio = await self.get_object(Audio, {'hashcode': hashcode})
            if self.obj_type_dest == "Server":
                audio, created = await self.get_or_create_object(
                    AudioInServer, {'audio': audio, 'server': server}, {'name': audio_name})
            elif self.obj_type_dest == "Channel" or self.obj_type_dest == "Member":
                entity, created = await self.get_or_create_object(
                    Entity, {'discord_id': self.discord_id_dest, 'server': server})
                audio, created = await self.get_or_create_object(
                    AudioInEntity, {'audio': audio, 'entity': entity}, {'name': audio_name})

            if not created:
                if self.discord_id_dest == ctx.message.author.id:
                    await self.embed_msg_with_interaction(
                        btn,
                        f"Hey {ctx.message.author.name}",
                        f"You already have this audio, please try again",
                        30
                    )
                else:
                    await self.embed_msg_with_interaction(
                        btn,
                        f"Hey {ctx.message.author.name}",
                        f"You can't copy this audio here, it already exists, please try again",
                        30
                    )
        else:
            await self.embed_msg_with_interaction(
                btn,
                f"I'm {ctx.message.author.name}",
                f"WavU is not joined to server destination, please use {config.prefix}help",
                30
            )

        return created

    async def valid_arguments(self, ctx, arg, arg2, arg3):

        valid = True
        self.discord_id_src = 0
        self.discord_id_dest = 0
        self.obj_type_src = None
        self.obj_type_dest = None

        if arg3 and valid:
            valid = await self.valid_server(ctx, arg3)
        else:
            self.server_id = ctx.guild.id
            valid = True

        if arg2 and valid:
            valid = await self.valid_arg(ctx, arg2)
            self.discord_id_dest = self.discord_id
            self.obj_type_dest = self.obj_type

        if valid:
            guild = self.client.get_guild(int(self.server_id))
            has_role = await self.role_required(ctx, guild)
            if not has_role:
                valid = False

        return valid

    @commands.command(aliases=['Copy', 'co', 'Co', 'share', 'Share', 'sh', 'Sh'])
    async def copy(self, ctx, arg=None, arg2=None, arg3=None):

        if not await self.user_input_valid(ctx, arg, arg2, arg3):
            return

        _, audios, hashcodes = await self.get_audios(ctx, arg)

        if audios:
            self.actual_page = 0

            self.list_audios = [audios[i:i + 10] for i in range(0, len(audios), 10)]
            self.page_len = len(self.list_audios)

            self.view = discord.ui.View()
            self.instruction_msg = f"Choose a _number_ to move a _**.mp3**_ file\n"
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
                            audio = audios[offset]
                            hashcode = hashcodes[offset]
                            valid = await self.copy_file(ctx, btn, audio, hashcode)
                            if valid:
                                await self.embed_msg_with_interaction(
                                    btn,
                                    f"{ctx.message.author.name} here is your file",
                                    f'**{audios[offset]}** has been _**moved**_',
                                    30
                                )
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
            hey_msg = content.hey_msg.format(username)
            await self.embed_msg(ctx, hey_msg, content.empty_list)
        RUNNING_COMMAND.remove(ctx.author)

    async def user_input_valid(self, ctx, arg=None, arg2=None, arg3=None):

        username = ctx.message.author.name.capitalize()
        sorry_msg = content.sorry_msg.format(username)

        if not await super().user_input_valid(ctx, arg):
            return

        if not arg or not arg2:
            wrong_value = content.wrong_value.format(config.prefix)
            await self.embed_msg(ctx, sorry_msg, wrong_value, 30)
            RUNNING_COMMAND.remove(ctx.author)
            return

        valid = await self.valid_arguments(ctx, arg, arg2, arg3)

        if not valid:
            return

        if self.discord_id_src and self.discord_id_src == self.discord_id_dest and self.server_id == ctx.guild.id:
            await self.embed_msg(ctx, sorry_msg, content.cant_copy, 30)
            RUNNING_COMMAND.remove(ctx.author)
            return

        if self.obj_type_dest == "Server" and self.discord_id_dest and self.discord_id_dest != self.server_id:
            await self.embed_msg(ctx, sorry_msg, content.cant_direct_copy, 30)
            RUNNING_COMMAND.remove(ctx.author)
            return

        return True


async def setup(client):
    await client.add_cog(CopyCommand(client))
