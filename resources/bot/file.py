# -*- coding: utf-8 -*-

'''
@staticmethod
    async def embed_list(self, ctx):

        dirnames_aux = []
        list_tab = []
        title_tab = ""
        file_tab = ""
        user_index = 0
        file_tabs = []
        filenames_list = []

        # Go through directories and get the user/channel id and base case get all the common files
        for (dirpath, dirnames, filenames) in walk(config.path + "/" + str(ctx.message.guild.id)):
            if dirnames:
                title_tab = "**Common:**\n"
                dirnames_aux = dirnames.copy()
            else:
                try:
                    user = await self.client.fetch_user(dirnames_aux[user_index])
                except:
                    user = None
                try:
                    channel = await self.client.fetch_channel(dirnames_aux[user_index])
                except:
                    channel = None

                if user:
                    title_tab = "**Member: " + user.name + "**\n"
                elif channel:
                    title_tab = "**Channel: " + channel.name + "**\n"

                user_index += 1

            filenames_list.append([filenames[i:i + 10] for i in range(0, len(filenames), 10)])

            # Enlist 10 first files on common files
            for index, filename in enumerate(filenames):
                if (index + 1) % 10 == 0:
                    file_tab = file_tab + str(10) + '. ' + filename + '\n'
                    file_tabs.append(file_tab)
                    file_tab = ""
                else:
                    file_tab = file_tab + str((index + 1) % 10) + '. ' + filename + '\n'
            if file_tab != "":
                file_tabs.append(file_tab)

            if file_tabs:
                list_tab.append([title_tab, file_tabs])
            file_tabs = []
            file_tab = ""

        return list_tab, filenames_list, dirnames_aux

    @staticmethod
    async def core_reactions(msg_em, filenames, dict_numbers):
        await msg_em.add_reaction('⬅️')
        await msg_em.add_reaction('❌')
        await msg_em.add_reaction('➡️')

        for ind in range(len(filenames[0][0])):
            await msg_em.add_reaction(dict_numbers[str(ind + 1)])
            await asyncio.sleep(0.1)

    @staticmethod
    async def change_page(index, jndex, reaction, embed, prev_pages_len, list_tab, msg_em, current_pages_len,
                          last_pages_len, first_pages_len):

        # index == Tab && jndex == Page
        # list_tab[tab][page]

        # Go left when tab is not on the first one
        if str(reaction.emoji) == "⬅️" and index > 0:
            embed.clear_fields()
            # Tab > 0 and Before Tab == 0 and Current page == 0
            if prev_pages_len == 0 and jndex == 0:
                print("left1")
                embed.add_field(
                    name=list_tab[index - 1][0] + str(prev_pages_len + 1) + '/' + str(prev_pages_len + 1),
                    value=list_tab[index - 1][1][0])
                index -= 1
                jndex = prev_pages_len
            # Tab > 0 and Before Tab > 0 and Current page == 0
            elif prev_pages_len > 0 and jndex == 0:
                print("left2")
                embed.add_field(
                    name=list_tab[index - 1][0] + str(prev_pages_len + 1) + '/' + str(prev_pages_len + 1),
                    value=list_tab[index - 1][1][prev_pages_len])
                index -= 1
                jndex = prev_pages_len
            # Tab > 0 and current page < 0
            elif jndex > 0:
                print("left3")
                embed.add_field(name=list_tab[index][0] + str(jndex) + '/' + str(current_pages_len),
                                value=list_tab[index][1][jndex - 1])
                jndex -= 1

            await msg_em.edit(embed=embed)
        # Go right when tab is not on the last one
        elif str(reaction.emoji) == "➡️" and index < len(list_tab) - 1:
            embed.clear_fields()
            # len(pages) == 0
            if len(list_tab[index][1]) - 1 == 0:
                print("right1")
                embed.add_field(name=list_tab[index + 1][0] + str(1) + '/' + str(len(list_tab[index + 1][1])),
                                value=list_tab[index + 1][1][0])
                jndex = 0
                index += 1
            # 0 < len(pages) < page(current)
            elif len(list_tab[index][1]) - 1 > 0 and len(list_tab[index][1]) - 1 > jndex:
                print("right2")
                embed.add_field(name=list_tab[index][0] + str(jndex + 2) + '/' + str(current_pages_len),
                                value=list_tab[index][1][jndex + 1])
                jndex += 1
            # 0 < len(pages) and len(pages) == page(current)
            elif 0 < len(list_tab[index][1]) - 1 == jndex:
                print("right3")
                embed.add_field(name=list_tab[index + 1][0] + str(1) + '/' + str(len(list_tab[index + 1][1])),
                                value=list_tab[index + 1][1][0])
                jndex = 0
                index += 1

            await msg_em.edit(embed=embed)
        # Go left when tab is on the first one
        elif str(reaction.emoji) == "⬅️" and index == 0:
            embed.clear_fields()
            # Tab == 0 and Before Tab == 0 and Current page == 0
            if jndex == 0:
                print("left4")
                embed.add_field(name=(list_tab[len(list_tab) - 1][0] + str(last_pages_len + 1) +
                                      '/' + str(last_pages_len + 1)),
                                value=list_tab[len(list_tab) - 1][1][last_pages_len])
                jndex = last_pages_len
                index = len(list_tab) - 1
            # Tab == 0 and page > 0
            elif jndex > 0:
                print("left5")
                embed.add_field(name=list_tab[index][0] + str(jndex) + '/' + str(current_pages_len),
                                value=list_tab[index][1][jndex - 1])
                jndex -= 1
            await msg_em.edit(embed=embed)
        elif str(reaction.emoji) == "➡️" and index == len(list_tab) - 1:
            embed.clear_fields()
            if len(list_tab[index][1]) - 1 == jndex:
                print("right4")
                embed.add_field(name=list_tab[0][0] + str(1) + '/' + str(first_pages_len + 1),
                                value=list_tab[0][1][0])
                index = 0
                jndex = 0
            elif len(list_tab[index][1]) - 1 > jndex:
                print("right5")
                embed.add_field(name=list_tab[index][0] + str(jndex + 2) + '/' + str(current_pages_len),
                                value=list_tab[index][1][jndex + 1])
                jndex += 1
            await msg_em.edit(embed=embed)

        return index, jndex

    @staticmethod
    async def arrows(self, ctx, list_tab, dict_numbers, filenames, dirnames, voice):

        def check(reaction, user):
            return user != self.client.user and user.guild.id == ctx.guild.id

        loop = self.client.loop or asyncio.get_event_loop()

        index = 0
        jndex = 0
        embed = discord.Embed(title='Choose a file to play', color=0xFC65E1)
        embed.add_field(name=list_tab[index][0] + str(jndex + 1) + '/' + str(len(list_tab[index][1])),
                        value=list_tab[index][1][0])
        msg_em = await ctx.send(embed=embed)

        task_core_reaction = loop.create_task(self.core_reactions(msg_em, filenames, dict_numbers))

        task_arrows = None

        while True:
            reaction, user = await self.client.wait_for('reaction_add', check=check)

            prev_pages_len = len(list_tab[index - 1][1]) - 1
            last_pages_len = len(list_tab[len(list_tab) - 1]) - 1
            current_pages_len = len(list_tab[index][1])
            first_pages_len = len(list_tab[0][1]) - 1

            index, jndex = await self.change_page(index, jndex, reaction, embed, prev_pages_len, list_tab, msg_em,
                                                  current_pages_len, last_pages_len, first_pages_len)

            if reaction:
                await asyncio.sleep(0.1)
                await msg_em.remove_reaction(emoji=reaction.emoji, member=user)

            if str(reaction.emoji) == "➡️" or str(reaction.emoji) == "⬅️":
                if task_arrows is not None:
                    await task_arrows
                if task_core_reaction is not None:
                    await task_core_reaction

                task_arrows = loop.create_task(self.arrows_reactions(index, jndex, filenames,
                                                                     task_arrows, msg_em, self.client.user,
                                                                     dict_numbers))

            if str(reaction.emoji) == '1️⃣' or str(reaction.emoji) == '2️⃣' or str(reaction.emoji) == '3️⃣' or \
                    str(reaction.emoji) == '4️⃣' or str(reaction.emoji) == '5️⃣' or str(reaction.emoji) == '6️⃣' or \
                    str(reaction.emoji) == '7️⃣' or str(reaction.emoji) == '8️⃣' or str(reaction.emoji) == '9️⃣' or \
                    str(reaction.emoji) == '🔟':
                await self.chosen_file(self, ctx, reaction, filenames, dirnames, index, jndex, dict_numbers)

            if str(reaction.emoji) == '❌':
                db.sound_pad_state(0, str(ctx.guild.id))
                await msg_em.delete()
                embed = discord.Embed(title='Soundpad is off', color=0xFC65E1)
                await ctx.send(embed=embed)
                await voice.disconnect()
                return

    @staticmethod
    async def arrows_reactions(index, jndex, filenames, prev_num_len, msg_em, user, dict_numbers):

        actual_num_len = filenames[index][jndex]

        if prev_num_len is None:
            prev_num_len = filenames[0][0]
        else:
            prev_num_len = prev_num_len.result()

        if len(actual_num_len) < len(prev_num_len):
            remove = len(prev_num_len) - len(actual_num_len)
            for ind in range(remove):
                await asyncio.sleep(0.1)
                await msg_em.remove_reaction(emoji=dict_numbers[str(len(prev_num_len) - ind)], member=user)
        else:
            add = len(actual_num_len) - len(prev_num_len)
            for ind in range(add):
                await asyncio.sleep(0.1)
                await msg_em.add_reaction(dict_numbers[str(len(prev_num_len) + ind + 1)])

        return actual_num_len

    @staticmethod
    async def chosen_file(self, ctx, reaction, filenames, dirnames, index, jndex, dict_numbers):
        loop = self.client.loop or asyncio.get_event_loop()
        if ctx.author.voice is None:
            await ctx.send("You need to be connected on a **Voice channel**")
            return

        songs = filenames[index][jndex]

        try:
            if index == 0:
                path_to_play = 'audio/' + str(ctx.message.guild.id) + '/' + \
                               str(songs[int(dict_numbers[str(reaction.emoji)]) - 1])
            else:
                path_to_play = 'audio/' + str(ctx.message.guild.id) + '/' + dirnames[index - 1] + '/' + \
                               str(songs[int(dict_numbers[str(reaction.emoji)]) - 1])

            voice = get(self.client.voice_clients, guild=ctx.author.guild)
            if str(ctx.guild.id) not in self.queue:
                await self.start_playing(self, ctx, voice, path_to_play)
            else:
                self.queue[str(ctx.guild.id)].append(path_to_play)
        except Exception as e:
            print(str(e))
            pass

    @staticmethod
    async def start_playing(self, ctx, voice, path_to_play):
        loop = self.client.loop or asyncio.get_event_loop()
        self.queue[str(ctx.guild.id)] = [path_to_play]

        i = 0
        while i < len(self.queue[str(ctx.guild.id)]):
            partial = functools.partial(voice.play, discord.FFmpegPCMAudio(self.queue[str(ctx.guild.id)][i]))
            await loop.run_in_executor(None, partial)
            while voice.is_playing():
                await asyncio.sleep(0.3)
            i += 1

        del self.queue[str(ctx.guild.id)]

    @commands.command(aliases=['sp', 'Soundpad', 'Sp', 'SP', 'SoundPad'])
    async def soundpad(self, ctx):

        has_role = await self.required_role(ctx)
        if not has_role:
            return

        if ctx.author.voice is None:
            await ctx.send("You need to be connected on a **Voice channel**")
            return

        db.sound_pad_state(1, str(ctx.guild.id))

        channel = ctx.author.voice.channel
        voice = await channel.connect()

        list_tab, filenames, dirnames = await self.embed_list(self, ctx)

        dict_numbers = {'1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣', '5': '5️⃣',
                        '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣', '10': '🔟',
                        '1️⃣': '1', '2️⃣': '2', '3️⃣': '3', '4️⃣': '4', '5️⃣': '5',
                        '6️⃣': '6', '7️⃣': '7', '8️⃣': '8', '9️⃣': '9', '🔟': '10'}

        await self.arrows(self, ctx, list_tab, dict_numbers, filenames, dirnames, voice)
'''
