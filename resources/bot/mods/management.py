# -*- coding: utf-8 -*-

import asyncio
import logging

from discord.ext import commands

import content
from resources.audio.models import Audio, AudioInServer
from resources.bot.helpers import Helpers
from resources.entity.models import Entity
from resources.server.models import Server


class Management(commands.Cog, Helpers):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).administrator:

                await guild.create_role(name='FM', reason="necessary to control bot's commands", mentionable=True)

                server, created = await self.get_or_create_object(Server, {'discord_id': guild.id})

                owner = await self.client.fetch_user(guild.owner_id)

                if created:

                    await owner.send(
                        f"Thanks {owner.name} for adding me to {guild.name}!\n"
                        "Here is my personal discord server if you want to be part of this community\n"
                        + content.server_link)

                    default_audios = [
                        ("1e8de08be93c4609075c8084a0425de8", "Anime WOW"),
                        ("13e4fd42a6d1145839565311261a94c3", "Best Cry Ever"),
                        ("27e4b3d10a131fd01514ceb98d1f7f06", "Deez Nuts"),
                        ("96d52d399501db46cf0fce1ac8e3a6bc", "DO YOU KNOW THE WAY"),
                        ("379b45d46268d6639a409a110d631989", "FBI Open Up"),
                        ("476a5cb713b2e3d6b00e6f9dccf4b477", "hello im under the water"),
                        ("921af1a487ae3a2eef535e0d457506bd", "Hello There Obi Wan"),
                        ("4993fc49ad04afb7305adea87089d699", "Hey Thats Pretty Good"),
                        ("61884d84d62b119923121e3d1b9fd1cb", "Michael Rosen Nice"),
                        ("acbc2e1ba4e22b2e1844a1b545ef6cbb", "Minecraft Door Open and Close"),
                        ("d74aa6021e465c9bbd3be22ae8915e49", "Roblox Death Sound"),
                        ("de9b9bbd6de13caa8f6f6fdbd5fa5621", "TADAAH")
                    ]

                    for audio_hashcode, audio_name in default_audios:
                        audio, _ = await self.get_or_create_object(Audio, {'hashcode': audio_hashcode})
                        audio, created = await self.get_or_create_object(AudioInServer,
                                                                         {'audio': audio, 'server': server},
                                                                         {'name': audio_name})

                else:
                    await owner.send(
                        f"Welcome back {owner.name}, happy to be back in {guild.name}!\n"
                        "Here is my personal discord server if you want to be part of this community\n"
                        + content.server_link)

    @commands.Cog.listener()
    async def on_member_join(self, member):

        entity, created = await self.get_or_create_object(Entity, {'discord_id': member.id})

        if created:
            logging.info(f'The server {member.guild.name} was joined')
            await self.embed_msg(member, f"Welcome to **{member.guild.name}**",
                                 "I'm wavU and i'll appear on *Voice channels* "
                                 "everytime someone joins in and play any random audio this server has. To know more "
                                 "about me, type **=help**. Have a nice day!")
        else:
            await self.embed_msg(member, f"Welcome to **{member.guild.name}**",
                                 f"Hey {member.name}, you already know me. You are able to use _copy_ command to "
                                 f"bring your audios to **{member.guild.name}** server (_FM_ Role required)")

        await asyncio.sleep(3 * 60 * 60)

        msgs = member.dm_channel
        async for msg in msgs.history(limit=10):
            if msg.author == self.client.user:
                await msg.delete()


def setup(client):
    client.add_cog(Management(client))
