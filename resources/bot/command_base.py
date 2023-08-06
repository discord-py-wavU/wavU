# Standard packages
import asyncio
import logging
import re
# Extras packages
from asgiref.sync import sync_to_async
# Discord packages
import discord
# Own packages
import config
import content
# Project packages
from resources.audio.models import Audio, AudioInEntity, AudioInServer
from resources.entity.models import Entity
from resources.server.models import Server

# Globals variables
CHOOSE_NUMBER = {'1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣', '5': '5️⃣',
                 '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣', '10': '🔟'}
RUNNING_COMMAND = set()


class Query:

    def __init__(self):
        super().__init__()

    # Get objects from queries methods

    @staticmethod
    async def get_or_create_object(obj, kwargs, default=None):
        return await sync_to_async(obj.objects.get_or_create, thread_sensitive=True)(**kwargs, defaults=default)

    @staticmethod
    async def filter_object(obj, kwargs):
        return await sync_to_async(obj.objects.filter, thread_sensitive=True)(**kwargs)

    async def get_object(self, obj, kwargs):
        try:
            objects = await self.filter_object(obj, kwargs)
            gotten_obj = await sync_to_async(lambda: objects.distinct().first(), thread_sensitive=True)()
        except Exception as e:
            logging.exception(e)
            gotten_obj = None
        return gotten_obj

    @staticmethod
    async def get_random_object(obj):
        return await sync_to_async(obj.objects.order_by('?').first(), thread_sensitive=True)()

    async def get_async_audio(self, async_obj, kwargs):
        objects = await self.filter_object(async_obj, kwargs)
        obj = await sync_to_async(lambda: objects.distinct().first(), thread_sensitive=True)()
        if obj:
            obj_audio = await obj.audios.order_by('?').afirst()
            return await sync_to_async(lambda: obj_audio.audio, thread_sensitive=True)()

    async def get_async_audio_list(self, async_obj, kwargs):
        audio_name_list = []
        audio_hashcode_list = []
        objects = await self.filter_object(async_obj, kwargs)
        async for obj in objects:
            audio_name_list.append(obj.name)
            hashcode = await sync_to_async(lambda: obj.audio.hashcode, thread_sensitive=True)()
            audio_hashcode_list.append(hashcode)
        return objects, audio_name_list, audio_hashcode_list

    async def get_audios(self, ctx, arg):

        server = await self.get_object(Server, {'discord_id': ctx.message.guild.id})
        is_server = False

        if arg:
            await self.get_id_from_mention(arg)
            is_server = self.client.get_guild(int(self.discord_id))

        if arg is None or is_server:
            obj, audio_name_list, audio_hashcode_list = await \
                self.get_async_audio_list(AudioInServer, {'server': server})
        else:
            entity, _ = await self.get_or_create_object(Entity, {'discord_id': self.discord_id, 'server': server})
            obj, audio_name_list, audio_hashcode_list = await \
                self.get_async_audio_list(AudioInEntity, {'entity': entity})

        return obj, audio_name_list, audio_hashcode_list

    async def get_id_from_mention(self, mention):
        value = re.findall(r'\b\d+\b', mention)
        if value:
            self.discord_id = int(value[0])


class Message:

    def __init__(self):
        super().__init__()
        self.instruction_msg = None
        self.list_audios = []
        self.actual_page = 0

    # Build message methods

    async def show_status_list(self, ctx):
        list_songs = ""
        for index, obj in enumerate(self.list_audios[self.actual_page]):
            emoji = ":white_check_mark:" if obj[1] else ":x:"
            list_songs = list_songs + f"{str(index + 1)}. {obj[0]} {emoji}\n"
        if list_songs:
            msg_name = f"List .mp3 files:"
            msg_value = f"{self.instruction_msg}{list_songs}"
            await self.embed_msg_with_view(ctx, msg_name, msg_value)

    async def show_audio_list(self, ctx):
        list_songs = ""
        for index, song in enumerate(self.list_audios[self.actual_page]):
            list_songs = list_songs + f"{str(index + 1)}. {song}\n"
        list_songs = f"{list_songs}cancel"
        msg_name = f"List .mp3 files:"
        msg_value = f"{self.instruction_msg}{list_songs}"
        await self.embed_msg_with_view(ctx, msg_name, msg_value)

    # Send message methods

    async def embed_msg_with_interaction(self, btn, name: str, value: str, delete: int = None):
        embed = discord.Embed(color=0xFC65E1)
        embed.add_field(name=name,
                        value=value,
                        inline=False)
        return await btn.response.send_message(embed=embed, delete_after=delete)

    async def embed_msg_with_view(self, ctx, name: str, value: str, delete: int = None):
        embed = discord.Embed(color=0xFC65E1)
        embed.add_field(name=name,
                        value=value,
                        inline=False)
        self.emb_msg = await ctx.send(embed=embed, view=self.view, delete_after=delete)

    async def embed_finish_msg(self, ctx, name: str, value: str, custom_view: discord.ui.View = None):
        embed = discord.Embed(color=0xFC65E1)
        embed.add_field(name=name,
                        value=value,
                        inline=False)
        await ctx.send(embed=embed, view=custom_view)

    async def embed_msg(self, ctx, name: str, value: str, delete: int = None):
        embed = discord.Embed(color=0xFC65E1)
        embed.add_field(name=name,
                        value=value,
                        inline=False)
        self.emb_msg = await ctx.send(embed=embed, delete_after=delete)

    # Edit message methods

    async def edit_message(self):
        list_songs = ""
        for index, song in enumerate(self.list_audios[self.actual_page]):
            list_songs = list_songs + f"{str(index + 1)}. {song}\n"
        list_songs = f"{list_songs}cancel"
        embed = discord.Embed(color=0xFC65E1)
        embed.add_field(name=f"List .mp3 files:",
                        value=f"{self.instruction_msg}{list_songs}",
                        inline=False)

        await self.emb_msg.edit(embed=embed, view=self.view)


class CommandBase(Query, Message):

    def __init__(self):
        super().__init__()
        self.queue = {}
        self.page_len = 0
        self.emb_msg = None
        self.view = None
        self.interaction = None
        self.discord_id = None
        self.server_id = None

    async def user_input_valid(self, ctx, arg=None):

        if not await self.command_lock(ctx):
            return False

        has_role = await self.role_required(ctx)
        if not has_role:
            RUNNING_COMMAND.remove(ctx.author)
            return False

        valid = await self.valid_arg(ctx, arg)
        if not valid:
            RUNNING_COMMAND.remove(ctx.author)
            return False

        return True

    async def get_interaction(self, btn):
        custom_id = btn.data.get('custom_id')
        if custom_id.isdigit():
            self.interaction = int(custom_id)
        else:
            self.interaction = custom_id

    async def move_page(self, btn):
        await self.add_interaction_buttons()
        await btn.response.defer()

    async def add_special_buttons(self, ctx):

        grey = discord.ButtonStyle.gray
        button = discord.ui.Button
        view = discord.ui.View()

        view.add_item(
            item=button(
                style=grey,
                label="Join Server",
                url=content.server_link,
                row=0
            )
        )
        view.add_item(
            item=button(
                style=grey, label="Add me to your server",
                url=content.invite_link,
                row=1
            )
        )

        username = ctx.message.author.name.capitalize()
        title = f"Thanks {username} for using wavU :wave:"
        await self.embed_finish_msg(ctx, title, "", view)

    # Button methods

    async def button_interactions(self):

        audios_len = len(self.list_audios[self.actual_page])
        grey = discord.ButtonStyle.gray
        button = discord.ui.Button

        arrow_rows = 2 if audios_len > 5 else 1

        self.view.add_item(item=button(style=grey, label="⬅️", custom_id="left", row=arrow_rows))
        self.view.add_item(item=button(style=grey, label="❌", custom_id="cancel", row=arrow_rows))
        self.view.add_item(item=button(style=grey, label="➡️", custom_id="right", row=arrow_rows))

        for ind in range(audios_len):
            row = self.get_row(ind)
            self.view.add_item(
                item=button(
                    style=grey,
                    label=CHOOSE_NUMBER[str(ind + 1)],
                    custom_id=str(ind + 1,),
                    row=row
                )
            )

    def get_row(self, ind):
        return 0 if ind < 5 else 1

    async def add_interaction_buttons(self):
        prev = self.actual_page
        self.actual_page = await self.choose_direction()

        await self.edit_message()

        if prev != self.actual_page:
            self.view.clear_items()
            await self.button_interactions()
            await self.emb_msg.edit(view=self.view)

    async def choose_direction(self):
        actual_page = self.actual_page
        if self.interaction == "right":
            actual_page = (self.actual_page + 1) % self.page_len
        elif self.interaction == "left":
            actual_page = (self.actual_page - 1) % self.page_len
        return actual_page

    # Checker methods

    async def command_lock(self, ctx):
        # Check if the user is in the set of running commands

        if ctx.author in RUNNING_COMMAND:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name} ",
                                 "You cannot use more than one command at once, "
                                 "please finish or cancel your current process", 30)
            # Return False if the user is already running a command
            return False
        else:
            # Add the user to the set of running commands
            RUNNING_COMMAND.add(ctx.author)

            # Return True if the user is not already running a command
            return True

    async def valid_person(self, ctx, arg):
        await self.get_id_from_mention(arg)
        valid = ctx.guild.get_member(self.discord_id)
        if not valid:
            self.discord_id = None
        else:
            self.obj_type = "Member"
        return valid

    async def valid_channel(self, ctx, arg):
        await self.get_id_from_mention(arg)
        valid = True
        if not self.server_id:
            self.server_id = ctx.guild.id
        guild = self.client.get_guild(self.server_id)
        voice_channels = guild.voice_channels
        name_channels_list = [voice_channel.name for voice_channel in voice_channels]
        if arg not in name_channels_list and not arg.isdigit():
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 f"This argument ({arg}) is not valid, please try again", 30)
            valid = False
        else:
            if arg.isdigit():
                channel = guild.get_channel(int(arg))
                if channel:
                    self.discord_id = channel.id
                else:
                    self.discord_id = None
            else:
                self.discord_id = voice_channels[name_channels_list.index(arg)].id
            if not self.discord_id:
                await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                     f"This argument ({arg}) is not a valid id, please try again", 30)
                valid = False

        return valid

    async def valid_arg(self, ctx, arg):
        if arg:
            self.discord_id = arg
            name_channels_list = []
            valid = await self.valid_person(ctx, arg)

            if not valid and arg.isdigit():
                valid = self.client.get_guild(int(arg))
                if valid:
                    self.discord_id = valid.id
                    self.obj_type = "Server"

            if not valid:
                valid = await self.valid_channel(ctx, arg)
                if valid:
                    self.obj_type = "Channel"
            if str(self.discord_id) not in arg and name_channels_list and arg not in name_channels_list:
                await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                     f"This format is wrong, please use **{config.prefix}help**", 30)
                valid = False
                self.obj_type = ""
                RUNNING_COMMAND.remove(ctx.author)
        else:
            valid = True
            self.discord_id = ctx.message.guild.id
            self.obj_type = "Server"

        return valid

    async def valid_server(self, ctx, arg):
        if arg.isdigit():
            guild = self.client.get_guild(int(arg))
            if guild:
                return True, guild.id
        else:

            guilds = self.client.guilds
            name_guilds_list = [guild.name for guild in guilds]
            if arg not in name_guilds_list:
                await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                     f"This is not a guild name, please try again", 30)
                return False
            else:
                self.discord_id = guilds[name_guilds_list.index(arg)].id
            if not self.discord_id:
                await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                     f"This guild id isn't valid, please try again", 30)
                return False

        return True

    async def role_required(self, ctx, guild=None):

        if not guild:
            roles = ctx.message.author.roles
            msg = f"You need _**FM**_ role to use this command.\n"
        else:
            roles = guild.get_member(ctx.message.author.id).roles
            msg = f"You need _**FM**_ role on _**{guild.name}**_ to use this command.\n"

        has_role = True
        if "FM" not in (roles.name for roles in roles):
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:", msg +
                                 "Only members who have administrator permissions are able to assign _**FM**_ role.\n"
                                 f"Command: \"**{config.prefix} role @mention**\"")
            has_role = False
            RUNNING_COMMAND.remove(ctx.author)

        return has_role
