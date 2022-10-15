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
field_description_add = f"*WavU* adds a mp3 file to selected files.\n" \
                        f"_Argument_:\n" \
                        f"*Optional:* `@mention`, `discord id` or `Voice name channel` (*default*: common files)\n"

field_title_choose = f"`{pre}choose` `{pre}ch` `{pre}c`"
field_description_choose = f"*WavU* chooses a mp3 file to play from selected files.\n" \
                           f"_Argument_:\n" \
                           f"*Optional:* `@mention`, `discord id` or `Voice name channel` (*default*: common files)\n"

field_title_download = f"`{pre}download` `{pre}dl`"
field_description_download = f"*WavU* downloads a mp3 file from selected files.\n" \
                             f"_Argument_:\n" \
                             f"*Optional:* `@mention`, `discord id` or `Voice name channel` (*default*: common files)\n"

field_title_copy = f"`{pre}copy` `{pre}share`"
field_description_copy = f"*WavU* copies a file from a person, channel or common server audios to another.\n" \
                         f"_Arguments_:\n" \
                         f"*Required:* `@mention`, `discord id` or `Voice name channel`\n" \
                         f"*Required:* `@mention`, `discord id` or `Voice name channel`\n" \
                         f"*Optional:* `server id` (*default*: this server)\n"

field_title_delete = f"`{pre}delete` `{pre}del` `{pre}remove` `{pre}rm`"
field_description_delete = f"*WavU* removes one mp3 file from selected files.\n" \
                           f"_Argument_:\n" \
                           f"*Optional:* `@mention`, `discord id` or `Voice name channel` (*default*: common files)\n"

field_title_edit = f"`{pre}edit`"
field_description_edit = f"*WavU* edits the name of one mp3 file from selected files.\n" \
                         f"_Argument_:\n" \
                         f"*Optional:* `@mention`, `discord id` or `Voice name channel` (*default*: common files)\n"

field_title_list = f"`{pre}list` `{pre}show`"
field_description_list = f"*WavU* shows all the mp3 files from selected files.\n" \
                         f"_Argument_:\n" \
                         f"*Optional:* `@mention`, `discord id` or `Voice name channel` (*default*: common files)\n"

field_title_volume = f"`{pre}volume` `{pre}vol`"
field_description_volume = f"*WavU* changes the mp3 file volume from one of selected files.\n" \
                           f"_Argument_:\n" \
                           f"*Optional:* `@mention`, `discord id` or `Voice name channel` (*default*: common files)\n"

field_title_stop = f"`{pre}stop` `{pre}disconnect` `{pre}disc` `{pre}shutup`"
field_description_stop = f"*WavU* silences the bot and disconnect it if it's in."

field_title_on = f"`{pre}on`"
field_description_on = f"*WavU* enable the feature of `<argument>`.\n" \
                       f"_Argument_:\n" \
                       f"*Required:* `common`, `channel`, `personal` or `all`\n"


field_title_off = f"`{pre}off`"
field_description_off = f"*WavU* disable the feature of `<argument>`.\n" \
                        f"_Argument_:\n" \
                        f"*Required:* `common`, `channel`, `personal` or `all`\n"

field_title_status = f"`{pre}status`"
field_description_status = f"*WavU* show all the status of the features."

field_title_role = f"`{pre}role @mention`"
field_description_role = f"*WavU* gives FM (File manager) role to a specific person." \
                         f"_Argument_:\n" \
                         f"*Required:* `@mention` or `discord id`(*default*: common files)\n"

field_title_unrole = f"`{pre}unrole @mention`"
field_description_unrole = f"*WavU* removes FM (File manager) role to a specific person.\n" \
                           f"_Argument_:\n" \
                           f"*Required:* `@mention` or `discord id`(*default*: common files)\n"

field_title_invite = f"Invite me"
field_description_invite = f'[Add me]({invite_link}) to your Discord server\n'

field_title_join = f"Join to my server"
field_description_join = f"Consider in joining to my [Discord server]({server_link}) too"
