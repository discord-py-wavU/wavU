import config

# Message content

thx_msg = "Thanks %s for using wavU :wave:"
hey_msg = "Hey %s"
empty_list = 'List is empty'
timeout = "Time is up!"
lock_value = "You cannot use more than one command at once, " + \
             "please finish or cancel your current process"
sorry_msg = "I'm sorry %s :cry:"
invalid_value = "This argument (%s) is not valid, please try again"
wrong_value = "This format is wrong, please use **%shelp**"
wrong_guild_id = "This is not a guild name, please try again"
wrong_guild_name = "This guild id is not valid, please try again"

need_fm_role = "You need to have FM role to use this command"
diff_fm_role = "You need _**FM**_ role on _**%s**_ to use this command.\n"
admin_perm = "Only members who have administrator permissions are able to assign _**FM**_ role.\n" + \
             "Command: \"**%s role @mention**\""

choose_number = "Choose _one_ number at a time:"

longer_video = "The entire video is longer than 10 seconds, please try again"
incorrect_format = "Incorrect format, please try again"
audio_len = "The audio segments should not surpass the file length, please try again"
audio_size = "This size of the audio is too large, **wavU** could not add it"
audio_unavailable = "The video was unavailable or does not exist, **wavU** could not add it"
check_audio = "The file duration is longer than 10 seconds or lower than 0, please try again"

cut_segment = "I need the audio segment to cut your audio\n" + \
              "Format: (**MM:SS:MS** to **MM:SS:MS**)\n" + \
              "MM = Minutes, SS = Seconds, MS = Milliseconds.\n" + \
              "If you want the entire audio type *entire*\n" + \
              "This segment must not be longer than 10 seconds."

working_file = "I'm working on your file"
processing_file = "Processing file... :gear: :tools:"
wait_sec = "Please wait a few seconds :hourglass:"
accept_file = "Would you like to keep this file?"
response_file_accept = "Type **yes** to keep it or **no** to cut it again, or **cancel**"

cant_copy = "You can't copy an audio in the same container"
cant_direct_copy = "You can't copy an audio to _common_ server files if server destination is different"

# Help command

img_link = "https://cdn.discordapp.com/attachments/721702337319665724/813869073388666921/WavU_b.png"
invite_link = "https://discord.com/oauth2/authorize?client_id=379158774159507459&scope=bot&permissions=268435496"
server_link = "https://discord.gg/qq6nQtGsyJ"
pre = config.prefix
bot_name = "wavU"
side_color = 0xFC65E1
emoji = "<:WavU:813997355975835669>"

title = f"{emoji} Hi everyone! My name is {bot_name} " \
        f"\nand I'm here to help you!"
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
