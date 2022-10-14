import config

img_link = "https://cdn.discordapp.com/attachments/721702337319665724/813869073388666921/WavU_b.png"
invite_link = "https://discord.com/oauth2/authorize?client_id=379158774159507459&scope=bot&permissions=268435496"
server_link = "https://discord.gg/qq6nQtGsyJ"
pre = config.prefix
bot_name = "wavU"
side_color = 0xFC65E1
emoji = "<:WavU:813997355975835669>"

title = f"{emoji} Hello everyone! My name is {bot_name} " \
        f"\nand i'm here to help you!"
description = "These are **all** the commands you can use\n\n" \
              "**Commands**"

field_title_add = f"`{pre}add` `{pre}a`"
field_description_add = f"__add__ adds a mp3 file to main files.\n" \
                        f"*Optional:* `@mention` adds a mp3 for a specific person.\n" \
                        f"*Optional:* `Voice channel` adds a mp3 for a specific channel.\n"

field_title_choose = f"`{pre}choose` `{pre}ch` `{pre}c`"
field_description_choose = f"__choose__ chooses a mp3 file to play from main files.\n" \
                           f"*Optional:* `@mention` chooses a mp3 to play from a specific person.\n" \
                           f"*Optional:* `Voice channel` chooses a mp3 to play from a specific channel.\n"

field_title_download = f"`{pre}download` `{pre}dl`"
field_description_download = f"__download__ downloads a mp3 file from main files.\n" \
                             f"*Optional:* `@mention` downloads a mp3 file from a specific person.\n" \
                             f"*Optional:* `Voice channel` downloads a mp3 file from a specific channel."

field_title_unzip = f"`{pre}unzip` "
field_description_unzip = f"__unzip__ unzips all the mp3 files in it to main files.\n" \
                          f"*Optional:* `@mention` unzips all the mp3 files in it to " \
                          f"a specific person.\n" \
                          f"*Optional:* `Voice channel` unzips all the mp3 files in it to " \
                          f"a specific channel.\n"

field_title_zip = f"`{pre}zip` `{pre}z`"
field_description_zip = f"__zip__ zips all the mp3 files saved in main files.\n" \
                        f"*Optional:* `@mention` zips all the mp3 files saved in a specific person.\n" \
                        f"*Optional:* `Voice channel` zips all the mp3 files saved in a specific channel."

field_title_delete = f"`{pre}delete` `{pre}del` `{pre}remove` `{pre}rm` "
field_description_delete = f"__delete__ removes one mp3 file from main files.\n" \
                           f"*Optional:* `@mention` removes one mp3 file from a specific person.\n" \
                           f"*Optional:* `Voice channel` removes one mp3 file from a specific channel."

field_title_edit = f"`{pre}edit`"
field_description_edit = f"__edit__ edits the name of one mp3 file from main files.\n" \
                         f"*Optional:* `@mention` edits the name of one mp3 file from a specific person.\n" \
                         f"*Optional:* `Voice channel` edits the name of one mp3 file from a specific channel."

field_title_list = f"`{pre}list` `{pre}show`"
field_description_list = f"__list__ shows all the mp3 files from main files.\n" \
                         f"*Optional:* `@mention` shows all the mp3 files from a specific person.\n" \
                         f"*Optional:* `Voice channel` shows all the mp3 files from a specific channel."

field_title_volume = f"`{pre}volume` `{pre}vol`"
field_description_volume = f"__volume__ changes the mp3 file volume from one main files.\n" \
                           f"*Optional:* `@mention`  changes the mp3 file volume from one specific person.\n" \
                           f"*Optional:* `Voice channel`  changes the mp3 file volume from one specific channel."

field_title_stop = f"`{pre}stop` `{pre}disconnect` `{pre}disc` `{pre}shutup`"
field_description_stop = f"__stop__ silences the bot and disconnect it if it's in."

field_title_on = f"`{pre}on <argument>` *arguments:* `common`, `channel`, `personal` or `all`"
field_description_on = f"__on__ enable the feature of `<argument>`."

field_title_off = f"`{pre}off <argument>` *arguments:* `common`, `channel`, `personal` or `all`"
field_description_off = f"__off__ disable the feature of `<argument>`"

field_title_status = f"`{pre}status`"
field_description_status = f"__show__ show all the status of the features."

field_title_role = f"`{pre}role @mention`"
field_description_role = f"__role__ gives FM (File manager) role to a specific person."

field_title_unrole = f"`{pre}unrole @mention`"
field_description_unrole = f"__unrole__ removes FM (File manager) role to a specific person."

field_title_invite = f"Invite me"
field_description_invite = f'[Add me]({invite_link}) to your Discord server\n'

field_title_join = f"Join to my server"
field_description_join = f"Consider in joining to my [Discord server]({server_link}) too"
