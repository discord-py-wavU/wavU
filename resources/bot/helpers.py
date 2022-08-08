import config

from resources.audio.models import Audio, AudioInEntity, AudioInServer
from resources.server.models import Server
from resources.entity.models import Entity
import asyncio
import discord
from asgiref.sync import sync_to_async


class Helpers:
    @staticmethod
    async def required_role(self, ctx):
        has_role = True
        if "FM" not in (roles.name for roles in ctx.message.author.roles):
            await self.embed_msg(ctx, f"I'm sorry {ctx.message.author.name} :cry:",
                                 f"You need _**FM**_ role to use this command.\n"
                                 "Only members who have administrator permissions are able to assign _**FM**_ role.\n"
                                 f"Command: \"**{config.prefix} role @mention**\"")
            has_role = False

        return has_role

    @staticmethod
    async def insert_file_db(self, ctx, arg: str, filename: str, hashcode: str):
        # TODO fix insert file

        import ipdb; ipdb.set_trace()

        if arg is None:
            audio, created = await sync_to_async(Audio.objects.get_or_create, thread_sensitive=True)(hashcode=hashcode)
            server, created = await sync_to_async(AudioInServer.objects.get_or_create, thread_sensitive=True)(audio=audio)
        else:
            audio, _ = Audio.objects.get_or_create(hashcode=hashcode)
            entity, _ = Entity.objects.get_or_create(ctx.message.author.id)
            server, created = AudioInEntity.objects.get_or_create(audio=audio, entity=entity)

        await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                             f"**{filename}** was added to **{ctx.message.guild.name}**")

    @staticmethod
    async def delete_message(msg, time: int):
        await asyncio.sleep(time)
        await msg.delete()

    @staticmethod
    async def embed_msg(ctx, name: str, value: str, delete: int = None):
        embed = discord.Embed(color=0xFC65E1)
        embed.add_field(name=name,
                        value=value,
                        inline=False)
        await ctx.send(embed=embed, delete_after=delete)

    @staticmethod
    def add_song(path, r):
        with open(path, 'wb') as f:
            for chunk in r.iter_content():
                if chunk:
                    f.write(chunk)
        f.close()