import sqlite3
import discord
from discord.ext import commands

def create_table():
    # Connect to database
    conn = sqlite3.connect('database.db')

    # Create a cursor
    c = conn.cursor()

    # Create Client Table
    c.execute('''CREATE TABLE servers (
                 server_name text,
                 state int
             )''')

    # Commit command
    conn.commit()

    # Close connection
    conn.close()


def add_server(server_name):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO servers VALUES (?,1)", (server_name,))

    conn.commit()
    conn.close()


def edit_server(state, server_name):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''UPDATE servers 
                SET state=?
                WHERE server_name=?
            ''', (state, server_name))

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


def server_delete(servername):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''DELETE FROM servers WHERE server_name=? 
            ''', (servername, ))

    conn.commit()
    conn.close()

class Status(commands.Cog):

    @commands.command(help="It will make the bot reproduces the .mp3 files")
    async def on(self, ctx):
        edit_server(1, str(ctx.message.guild.name))
        await ctx.send("Pepebot is online now")

    @commands.command(help="It will make the bot doesn't reproduce the .mp3 files")
    async def off(self, ctx):
        edit_server(0, str(ctx.message.guild.name))
        await ctx.send("Pepebot is offline now")

    @commands.command()
    async def status(self, ctx):
        servers = all_servers(False)
        for server in servers:
            if server[1] == ctx.message.guild.name:
                if server[2]:
                    await ctx.send("Pepebot is online")
                else:
                    await ctx.send("Pepebot is offline")

#    @commands.command()
#    async def serv(self, ctx):
#        await ctx.send(all_servers(True))


def setup(client):
    client.add_cog(Status(client))