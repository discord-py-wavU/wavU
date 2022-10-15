import glob
import logging
from os.path import join, dirname, isfile, basename

import discord.utils
from discord.ext import commands
from django.core.management.base import BaseCommand

import config
import content

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix=config.prefix, help_command=None, intents=intents)


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


class Command(BaseCommand):
    help = 'Runs the Discord bot'

    def handle(self, *args, **options):

        print("Starting bot...\n")
        print("Importing modules:")
        modules = glob.glob(join(dirname(__file__), "..", "..", "mods", "*.py"))
        for f in modules:
            if isfile(f) and not f.endswith("__init__.py"):
                print("   %s ... " % basename(f)[:-3], end="")
                client.load_extension(f"resources.bot.mods.{basename(f)[:-3]}")
                print(f"[OK]")

        print("")
        print("Modules loaded")

        client.run(config.token)
