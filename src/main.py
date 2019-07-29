import json
import discord
import requests

from sys import argv
from asyncio import sleep
from discord.ext.commands import Bot, Context
from discord import Embed

# local imports
from imports import sql
from imports.utils import Utils, vipId

config = json.load(open("config/config.json"))
twitch = json.load(open("config/twitch.json"))
# settings = sql.create_connection("../config/settings.db")
# c = settings.cursor()


__version__ = config["meta"]["version"][1:]

bot = Bot(command_prefix=config["bot"]["prefix"],
          case_insensitive=True,
          description=config["bot"]["description"],
          owner_ids=config["devs"],
          activity=discord.Activity(type=discord.ActivityType.playing, name="games with the Bean Gang.")
    )

u = Utils(config)

guild: discord.Guild

# roles
vipRole: discord.Role
streamerRole: discord.Role
beansRole: discord.Role

# channels
changelogChannel: discord.TextChannel
welcomeChannel: discord.TextChannel
streamerChannel: discord.TextChannel

newline = "\n\t- "

# Create table
# c.execute('''CREATE TABLE IF NOT EXISTS USERS
#              (USERNAME text, DISCRIMINATOR integer, ID integer, LEVEL integer)''')


@bot.event
async def on_ready():
    global guild
    global vipRole
    global streamerRole
    global beansRole
    global changelogChannel
    global welcomeChannel
    global streamerChannel

    guild = bot.get_guild(601701439995117568)

    # roles
    vipRole = guild.get_role(vipId)
    streamerRole = guild.get_role(601710639068610578)
    beansRole = guild.get_role(601711999939903489)

    # channels
    changelogChannel = bot.get_channel(603279565439369236)
    welcomeChannel = bot.get_channel(603284631151706112)
    streamerChannel = bot.get_channel(604088400819126361)

    print("BeanBot logged in...")
    if "--debug" not in argv:
        await changelogChannel.send(f"""
***BeanBot {config['meta']['version']} online!***
Recent Changes:
\t- {newline.join(config['meta']['changelog'])}
        """)


@bot.event
async def on_member_join(user: discord.Member):
    await user.add_roles(beansRole)

    await welcomeChannel.send(f"Welcome to the Bean Gang, {user.mention}")


@bot.event
async def on_member_remove(user: discord.Member):
    await welcomeChannel.send(f"The bean gang will miss you, {user.display_name}")
    await user.send(f"The bean gang will miss you!", tts=True)


async def background_loop():
    global twitch
    global config
    global guild
    global streamerChannel
    await sleep(10)
    await bot.wait_until_ready()
    while not bot.is_closed():
        for streamer in twitch["channels"]:
            r = requests.get(f"https://api.twitch.tv/helix/streams?user_login={streamer}",
                             headers={"Client-ID": config["secrets"]["twitchToken"]})

            streamData = r.json()
            print(streamData)

            if streamData["data"]:
                streamData = r.json()["data"]
                r = requests.get(f"https://api.twitch.tv/helix/users?id={streamData[0]['user_id']}",
                                 headers={"Client-ID": config["secrets"]["twitchToken"]})
                userData = r.json()["data"]
                r = requests.get(f"https://api.twitch.tv/helix/games?id={streamData[0]['game_id']}",
                                 headers={"Client-ID": config["secrets"]["twitchToken"]})
                gameData = r.json()["data"]

                embed = discord.Embed(title=streamData[0]["title"], url=f"https://twitch.tv/{streamer}",
                                      color=0x8000ff)
                embed.set_author(name=f"{streamer}",
                                 icon_url=userData[0]["profile_image_url"].format(width=500, height=500))
                embed.set_thumbnail(url=gameData[0]["box_art_url"].format(width=390, height=519))
                embed.set_image(url=streamData[0]["thumbnail_url"].format(width=1280, height=720))
                embed.add_field(name="Game", value=gameData[0]["name"], inline=True)
                embed.add_field(name="Viewers", value=streamData[0]["viewer_count"], inline=True)
                if streamer not in twitch["messages"]:
                    msg = await streamerChannel.send(f"@everyone {streamer} is live!", embed=embed)
                    twitch["messages"][streamer] = msg.id
                elif twitch["responses"][streamer] != streamData[0]:
                    msg = await streamerChannel.fetch_message(twitch["messages"][streamer])
                    await msg.edit(embed=embed)
                twitch["responses"][streamer] = streamData
                u.editConfig("twitch.json", twitch)
                twitch = u.reloadConfig("twitch.json")

            else:
                if streamer in twitch["messages"]:
                    msg = await streamerChannel.fetch_message(twitch["messages"][streamer])
                    await msg.delete()
                    del twitch["messages"][streamer]
                    u.editConfig("twitch.json", twitch)
                    twitch = u.reloadConfig("twitch.json")

            r.close()
        await sleep(60)


@bot.command()
async def raid(ctx:Context, twitchChannel:str = None):
    await ctx.message.delete()
    if not u.vip(ctx.author):
        msg = await ctx.send(f"{ctx.author.mention}, only VIPs can use this command.")
        await sleep(3)
        await msg.delete()
        return

    if not twitchChannel:
        msg = await ctx.send(f"{ctx.author.mention}, please specify a channel name.")
        await sleep(2)
        await msg.delete()
        return
    await ctx.send(f"@everyone we're raiding https://twitch.tv/{twitchChannel}")

@bot.command(name="vip")
async def _vip(ctx, _user: discord.Member = None):
    await ctx.message.delete()
    if not u.vip(ctx.author):
        msg = await ctx.send(f"{ctx.author.mention}, only VIPs can use this command.")
        await sleep(3)
        await msg.delete()
        return

    if not _user:
        msg = await ctx.send(f"{ctx.author.mention}, please tag a user to make them a VIP.")
        await sleep(2)
        await msg.delete()
        return

    if vipRole in _user.roles:
        msg = await ctx.send(f"{ctx.author.mention}, that user is already a VIP.")
        await sleep(2)
        await msg.delete()
        return

    await _user.add_roles(vipRole)
    await ctx.send(f"{_user.mention}, {ctx.author.mention} has made you a VIP!")

@bot.command(name="streamer")
async def _streamer(ctx, _user: discord.Member = None, _username: str = None):
    await ctx.message.delete()
    if not u.vip(ctx.author):
        msg = await ctx.send(f"{ctx.author.mention}, only VIPs can use this command.")
        await sleep(3)
        await msg.delete()
        return

    if not _user:
        msg = await ctx.send(f"{ctx.author.mention}, please tag a user to make them a streamer.")
        await sleep(2)
        await msg.delete()
        return

    if not _username:
        msg = await ctx.send(f"{ctx.author.mention}, please specify the users Twitch username.")
        await sleep(2)
        await msg.delete()
        return

    if vipRole in _user.roles:
        msg = await ctx.send(f"{ctx.author.mention}, that user is already a streamer.")
        await sleep(2)
        await msg.delete()
        return

    await _user.add_roles(streamerRole)
    twitch["channels"].append(_username)
    twitch["responses"][_username] = {}
    await ctx.send(f"{_user.mention}, {ctx.author.mention} has made you a streamer!")

# developer commands

@bot.command(name="dev")
async def _dev(ctx, _user: discord.Member = None):
    await ctx.message.delete()
    if not u.dev(ctx.author):
        msg = await ctx.send(f"{ctx.author.mention}, only developers can use this command.")
        await sleep(3)
        await msg.delete()
        return

    if not _user:
        msg = await ctx.send(f"{ctx.author.mention}, please tag a user to make them a developer.")
        await sleep(2)
        await msg.delete()
        return

    global config
    if _user.id in config["devs"]:
        msg = await ctx.send(f"{ctx.author.mention}, that user is already a developer.")
        await sleep(2)
        await msg.delete()
        return

    config["devs"].append(_user.id)
    config = u.reloadConfig()
    await ctx.send(f"{_user.mention}, {ctx.author.mention} has made you a developer!")


@bot.command()
async def reload(ctx, _config:str = str()):
    await ctx.message.delete()
    if not u.dev(ctx.author):
        msg = await ctx.send(f"{ctx.author.mention}, only developers can use this command.")
        await sleep(3)
        await msg.delete()
        return
    if _config.lower() == "config" or _config.lower() == "c":
        global config
        config = u.reloadConfig()
        msg = await ctx.send(f"{ctx.author.mention}, reloaded config!")
        await sleep(1)
        await msg.delete()
        return
    else:
        global settings
        settings.commit()
        settings.close()
        # settings = sql.create_connection("/config/settings.db")
        # global c
        # c = settings.cursor()
        msg = await ctx.send(f"{ctx.author.mention}, reloaded settings database!")
        await sleep(1)
        await msg.delete()
        return

@bot.command()
async def stop(ctx):
    await ctx.message.delete()
    if not u.dev(ctx.author):
        msg = await ctx.send(f"{ctx.author.mention}, only developers can use this command.")
        await sleep(3)
        await msg.delete()
        return
    msg = await ctx.send(f"Goodbye...")
    await sleep(1)
    await msg.delete()
    await bot.logout()
    # settings.commit()
    # settings.close()
    exit(1)


if __name__ == "__main__":
    bot.loop.create_task(background_loop())
    bot.run(config["secrets"]["token"])
    # settings.commit()
    # settings.close()