import sqlite3

from discord.ext import commands


def create_table():
    # Connect to database
    conn = sqlite3.connect('database.db')

    # Create a cursor
    c = conn.cursor()

    # Create Client Table
    c.execute('''CREATE TABLE servers (
                 server_id int,
                 serv_state int,
                 chan_state int,
                 per_state int
             )''')

    # Commit command
    conn.commit()

    # Close connection
    conn.close()


def add_server(server_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO servers VALUES (?,1,0,1)", (server_id,))

    conn.commit()
    conn.close()


def edit_server(state, server_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''UPDATE servers 
                 SET serv_state=?
                 WHERE server_id=?
            ''', (state, server_id))

    conn.commit()
    conn.close()


def edit_channel(state, server_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''UPDATE servers 
                 SET chan_state=?
                 WHERE server_id=?
            ''', (state, server_id))

    conn.commit()
    conn.close()


def edit_personal(state, server_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''UPDATE servers 
                 SET per_state=?
                 WHERE server_id=?
              ''', (state, server_id))

    conn.commit()
    conn.close()


def all_servers(show):
    conn = sqlite3.connect('database.db')

    c = conn.cursor()

    c.execute("SELECT rowid, * FROM servers")
    items = c.fetchall()

    if show:
        for item in items:
            print(item)

    conn.commit()

    conn.close()

    return items


def server_delete(server_id, id=None):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if id is not None:
        c.execute('''DELETE FROM servers WHERE server_id=? AND rowid=?
                  ''', (server_id, id))
    else:
        c.execute('''DELETE FROM servers WHERE server_id=?
                  ''', (server_id,))
    conn.commit()
    conn.close()


def edit_all(state, server_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''UPDATE servers 
                 SET per_state=?, chan_state=?, serv_state=?
                 WHERE server_id=?
              ''', (state, state, state, server_id))

    conn.commit()
    conn.close()


class Status(commands.Cog):

    @commands.command(alieses=['On'])
    async def on(self, ctx, arg=None):
        if "FM" not in (roles.name for roles in ctx.message.author.roles):
            await ctx.send("You need _**FM**_ role to use this command.\nOnly members who have "
                           + "administrator permissions are able to assign _**FM**_ role."
                           + "\nCommand: \"**" + config.prefix + "role @mention**\"")
        else:
            if arg == "common":
                edit_server(1, str(ctx.message.guild.id))
                await ctx.send("**wavU** is online for common :white_check_mark:")
            elif arg == "channel":
                edit_channel(1, str(ctx.message.guild.id))
                await ctx.send("**wavU** is online for channels :white_check_mark:")
            elif arg == "personal":
                edit_personal(1, str(ctx.message.guild.id))
                await ctx.send("**wavU** is online for personal :white_check_mark:")
            elif arg == "all":
                edit_all(1, str(ctx.message.guild.id))
                await ctx.send("**wavU** is online for common :white_check_mark:\n" +
                               "**wavU** is online for channels :white_check_mark:\n" +
                               "**wavU** is online for personal :white_check_mark:")
            elif arg is None:
                await ctx.send('Argument is needed, *options:* **common**, **channel**, **personal** or **all**')
            else:
                await ctx.send('Argument invalid, *options:* **common**, **channel**, **personal** or **all**')

    @commands.command(alieses=['Off'])
    async def off(self, ctx, arg=None):
        if "FM" not in (roles.name for roles in ctx.message.author.roles):
            await ctx.send("You need _**FM**_ role to use this command.\nOnly members who have "
                           + "administrator permissions are able to assign _**FM**_ role."
                           + "\nCommand: \"**" + config.prefix + "role @mention**\"")
        else:

            if arg == "common":
                edit_server(0, str(ctx.message.guild.id))
                await ctx.send("**wavU** is offline for common :x:")
            elif arg == "channel":
                edit_channel(0, str(ctx.message.guild.id))
                await ctx.send("**wavU** is offline for channels :x:")
            elif arg == "personal":
                edit_personal(0, str(ctx.message.guild.id))
                await ctx.send("**wavU** is offline for personal :x:")
            elif arg == "all":
                edit_all(0, str(ctx.message.guild.id))
                await ctx.send("**wavU** is offline for common :x:\n" +
                               "**wavU** is offline for channels :x:\n" +
                               "**wavU** is offline for personal :x:")
            elif arg is None:
                await ctx.send('Argument is needed, *options:* **common**, **channel**, **personal** or **all**')
            else:
                await ctx.send('Argument invalid, *options:* **common**, **channel**, **personal** or **all**')

    @commands.command()
    async def status(self, ctx):
        servers = all_servers(False)
        status = ""
        for server in servers:
            if server[1] == ctx.message.guild.id:
                if server[2]:
                    status = status + "**wavU** is **online** for common :white_check_mark:\n"
                else:
                    status = status + "**wavU** is **offline** for common :x:\n"
                if server[3]:
                    status = status + "**wavU** is **online** for channel :white_check_mark:\n"
                else:
                    status = status + "**wavU** is **offline** for channel :x:\n"
                if server[4]:
                    status = status + "**wavU** is **online** for personal :white_check_mark:\n"
                else:
                    status = status + "**wavU** is **offline** for personal :x:\n"

                await ctx.send(status)


def setup(client):
    client.add_cog(Status(client))
