# Standard imports
import asyncio
import glob
import logging
# Extra imports
from os.path import join, dirname, isfile, basename
# Discord imports
import discord.utils
from discord.ext import commands
from django.core.management.base import BaseCommand
# Own imports
import content
import config
from config import client
# Project imports
from resources.bot.command_base import Message

logging.basicConfig(level=logging.DEBUG)


@client.command(aliases=['Help'])
async def help(ctx):
    embed = discord.Embed(title=content.title, description=content.description, color=content.side_color)
    embed.set_thumbnail(url=content.img_link)
    embed.add_field(name=content.field_title_add, value=content.field_description_add, inline=False)
    embed.add_field(name=content.field_title_choose, value=content.field_description_choose, inline=False)
    embed.add_field(name=content.field_title_download, value=content.field_description_download, inline=False)
    embed.add_field(name=content.field_title_copy, value=content.field_description_copy, inline=False)
    embed.add_field(name=content.field_title_delete, value=content.field_description_delete, inline=False)
    embed.add_field(name=content.field_title_edit, value=content.field_description_edit, inline=False)
    embed.add_field(name=content.field_title_list, value=content.field_description_list, inline=False)
    embed.add_field(name=content.field_title_volume, value=content.field_description_volume, inline=False)
    embed.add_field(name=content.field_title_stop, value=content.field_description_stop, inline=False)
    embed.add_field(name=content.field_title_on, value=content.field_description_on, inline=False)
    embed.add_field(name=content.field_title_off, value=content.field_description_off, inline=False)
    embed.add_field(name=content.field_title_status, value=content.field_description_status, inline=False)
    embed.add_field(name=content.field_title_role, value=content.field_description_role, inline=False)
    embed.add_field(name=content.field_title_unrole, value=content.field_description_unrole, inline=False)
    embed.add_field(name=content.field_title_invite, value=content.field_description_invite, inline=False)
    embed.add_field(name=content.field_title_join, value=content.field_description_join, inline=False)
    await ctx.send(embed=embed)


@staticmethod
async def buttons(amount):
    view = discord.ui.View()
    style = discord.ButtonStyle.gray
    for i in range(amount):
        item = discord.ui.Button(style=style, label=str(i), custom_id=str(i))
        view.add_item(item=item)
    return view


@client.command()
async def pepi(ctx):
    await ctx.send(f"Hi We're glad you're here!")

    view = await buttons(5)
    await ctx.send("This is a test", view=view)

    btn = await client.wait_for('interaction', timeout=20)
    await btn.response.send_message("Button clicked")

    await ctx.send(f"You clicked {btn.data.get('custom_id')} button")

    if await view.interaction_check(btn):
        await ctx.send("View is done")


@client.event
async def on_ready():
    await client.change_presence(status=config.status, activity=discord.Game(config.game))
    logging.info("Bot is ready")


@client.command(aliases=['serv', 'ser'])
async def servers(ctx, arg=None):
    guilds = client.guilds

    if arg == "names":
        guilds = [guild.name for guild in guilds]
        await ctx.send(guilds)
    elif arg is None:
        await ctx.send("Amount of servers wavU is in: " + str(len(guilds)))
    else:
        await ctx.send("No valid argument")


@client.command()
async def ext(ctx, arg=None):
    if arg:
        try:
            logging.info(f"Module to reaload: {arg}")
            await client.reload_extension(f"resources.bot.mods.{arg}")
            await ctx.send("OK")
            logging.info("[OK]")
        except commands.errors.ExtensionNotLoaded:
            await ctx.send("This module could not be reload")
            logging.info("This module could not be reload")

    else:
        logging.info("Reloading")
        modules = glob.glob(join(dirname(__file__), "..", "..", "mods", "*.py"))
        for f in modules:
            try:
                if isfile(f) and not f.endswith("__init__.py"):
                    logging.info(basename(f)[:-3])
                    await client.reload_extension(f"resources.bot.mods.{basename(f)[:-3]}")
                    logging.info(f"[OK]")
            except commands.errors.ExtensionNotLoaded:
                await ctx.send(f"This {basename(f)[:-3]} module could not be reload")
                logging.info(f"This {basename(f)[:-3]} module could not be reload")

        logging.info("Modules loaded")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        msg_name = f"I'm sorry {ctx.message.author.name} :cry:"
        msg_value = f"{error}"
        await Message().embed_msg(ctx, msg_name, msg_value, 30)


class Command(BaseCommand):
    help = 'Runs the Discord bot'

    def handle(self, *args, **options):

        logging.info("Starting bot...")
        logging.info("Importing modules:")
        modules = glob.glob(join(dirname(__file__), "..", "..", "mods", "*.py"))
        for f in modules:
            if isfile(f) and not f.endswith("__init__.py"):
                logging.info(f"Module to reaload: {basename(f)[:-3]}")
                asyncio.run(client.load_extension(f"resources.bot.mods.{basename(f)[:-3]}"))
                logging.info(f"[OK]")
        logging.info("Modules loaded")

        client.run(config.token)
