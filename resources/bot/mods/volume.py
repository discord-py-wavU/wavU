import asyncio

from asgiref.sync import sync_to_async
from discord.ext import commands

from resources.bot.helpers import Helpers


class VolumeCommand(commands.Cog, Helpers):

    def __init__(self, client):
        self.client = client

    @staticmethod
    async def set_volume_obj_and_file(obj, volume):
        return await sync_to_async(obj.update, thread_sensitive=True)(volume=volume)

    @staticmethod
    async def get_volume_obj_and_file(obj, hashcode):
        return await sync_to_async(obj.filter, thread_sensitive=True)(audio__hashcode=hashcode)

    @commands.command()
    async def change_volume(self, ctx, audios, msg_number, obj, hashcode):

        def check_volume(m):
            return (m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                   or str(m.content).lower() == "cancel"

        volume_objs = await self.get_volume_obj_and_file(obj, hashcode)
        volume_obj = await volume_objs.afirst()
        await self.embed_msg(ctx, f"This is the current volume: {int(volume_obj.volume)}",
                             "Choose a number **(0-100)** or **cancel**")

        while True:
            msg_volume = await self.client.wait_for('message', check=check_volume, timeout=60)

            if str(msg_volume.content).lower() == "cancel":
                await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                     "_**Volume**_ has not been changed", 30)

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
                    await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                         f'**{audios[int(msg_number.content) - 1]} has been changed to** '
                                         f'**{str(msg_volume.content)}**', 30)
                    break
                else:
                    await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                         "That **volume** is not valid, try again", 30)
                    continue
            else:
                await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                     "That is not a number, try again", 30)
                continue

    @commands.command(aliases=['vol', 'Volume', 'Vol'])
    async def volume(self, ctx, arg=None):

        has_role = await self.required_role(self, ctx)
        if not has_role:
            return

        obj, audios, hashcodes = await self.search_songs(self, ctx, arg)

        if audios:

            msg = "Choose a _number_ to edit a _**.mp3**_ file _name_\n"

            await self.show_audio_list(self, ctx, audios, msg)

            def check_number(m):
                return (m.content.isdigit() and
                        m.author.guild.id == ctx.message.guild.id and m.author.id == ctx.message.author.id) \
                       or str(m.content).lower() == "cancel" \
                       or str(m.content).lower() == "all"

            try:
                for i in range(3):
                    msg_number = await self.client.wait_for('message', check=check_number, timeout=60)
                    if msg_number.content.isdigit() and int(msg_number.content) <= len(audios) \
                            and int(msg_number.content) != 0:
                        hashcode = hashcodes[int(msg_number.content) - 1]
                        await self.change_volume(ctx, audios, msg_number, obj, hashcode)
                        break

                    elif str(msg_number.content).lower() == "cancel":
                        await self.embed_msg(ctx, f"Thanks {ctx.message.author.name} for using wavU :wave:",
                                             "_**Volume**_ has not been changed", 30)
                        break
                    elif msg_number.content.isdigit() and \
                            (int(msg_number.content) > len(audios) or int(msg_number.content) == 0):
                        await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                             "That number is not an option. Try again **(" + str(i + 1) + "/3)**", 10)
                        if i == 2:
                            await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:",
                                                 "None of the attempts were correct, _**volume**_ has been aborted",
                                                 10)
            except asyncio.TimeoutError:
                await self.embed_msg(ctx, f"I'm sorry, {ctx.message.author.name} :cry:", "Time is up!", 15)
        else:
            await self.embed_msg(ctx, f"Hey {ctx.message.author.name}", "_List is empty_", 10)


def setup(client):
    client.add_cog(VolumeCommand(client))
