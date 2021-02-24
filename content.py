import config

img_link = "https://cdn.discordapp.com/attachments/721702337319665724/812507322873413672/prof_photo.png"
invite_link = "https://discord.com/oauth2/authorize?client_id=379158774159507459&scope=bot&permissions=268435496"
server_link = "https://discord.gg/hQF22MhC8P"
pre = config.prefix
bot_name = "wavU"
side_color = 0xFC65E1
emoji = ":wave:"

title = f"{emoji} Hello! I'm {bot_name}!"
description = "This is the list of commands you can use\n\n" \
              "**Commands**"

field_title_add = f"`{pre}add` `{pre}a`"
field_description_add = f"__add__ adds a mp3 file to main files.\n" \
                        f"*Optional:* `@mention` adds a mp3 for a specific person.\n"

field_title_unzip = f"`{pre}unzip`"
field_description_unzip = f"__unzip__ asks for a zip file to unzip it and add all the mp3 files in it to main files.\n" \
                          f"*Optional:* `@mention` asks for a zip file to unzip it and add all the mp3 files in it to " \
                          f"mentioned person.\n"

field_title_zip = f"`{pre}zip`"
field_description_zip = f"__zip__ zips all the mp3 files saved of main files.\n" \
                        f"*Optional:* `@mention` zips all the mp3 files saved of mentioned person."

field_title_delete = f"`{pre}delete` `{pre}dlt` `{pre}d` `{pre}del` `{pre}remove` `{pre}rm`"
field_description_delete = f"__delete__ removes one mp3 file from main files.\n" \
                           f"*Optional:* `@mention` deletes one mp3 file from mentioned person."

field_title_edit = f"`{pre}edit`"
field_description_edit = f"__edit__ edits the name of one mp3 file from main files.\n" \
                         f"*Optional:* `@mention` edits the name of one mp3 file from mentioned person."

field_title_list = f"`{pre}list` `{pre}show`"
field_description_list = f"__list__ shows all the mp3 files from main files.\n" \
                         f"*Optional:* `@mention` shows all the mp3 files from a mentioned person."

field_title_on = f"`{pre}on`"
field_description_on = f"__on__ turns on the bot."

field_title_off = f"`{pre}off`"
field_description_off = f"__off__ turns off the bot."

field_title_status = f"`{pre}status`"
field_description_status = f"__show__ show the bot status"

field_title_role = f"`{pre}role @mention`"
field_description_role = f"__role__ gives FM (File manager) role to mentioned person."

field_title_unrole = f"`{pre}unrole @mention`"
field_description_unrole = f"__unrole__ removes FM (File manager) role to mentioned person."

field_title_invite = f"Invite me"
field_description_invite = f'[Add me]({invite_link}) to your Discord server\n'

field_title_join = f"Join to my server"
field_description_join = f"Consider in joining to my [Discord server]({server_link}) too"