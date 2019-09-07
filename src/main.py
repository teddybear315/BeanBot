import time
import json
import discord
import requests

from sys import argv
from asyncio import sleep
from discord import Embed
from discord.ext.commands import Bot
from pymongo.collection import Collection


# local imports
from imports.twitch_integration import Twitch
from imports import twitch, u, config, secrets

twitch: Collection  = twitch()
config              = config()
secrets             = secrets()
u                   = u()

__version__ = config["meta"]["version"]
__authors__ = ["Yung Granny#7728", "Luke#1000"]

initial_extensions = [
    'cogs.twitch',
    'cogs.utilities'
]

prefix = config["bot"]["prefix"]
if "--debug" in argv:
    prefix = config["bot"]["dev_prefix"]


bot = Bot(command_prefix=prefix,
        case_insensitive=True,
        description=config["bot"]["description"],
        owner_ids=config["devs"],
        activity=discord.Activity(
        type=discord.ActivityType.playing, name="games with the Bean Gang.")
)

t = Twitch(config, secrets, twitch, bot)
guild: discord.Guild

# roles
vipRole     : discord.Role
streamerRole: discord.Role
beansRole   : discord.Role

# channels
changelogChannel    : discord.TextChannel
welcomeChannel      : discord.TextChannel
streamerChannel     : discord.TextChannel
suggestionChannel   : discord.TextChannel

newline = "\n\t- "

@bot.event
async def on_ready():
    u.log("Bot ready...")
    u.log("Running version: " + __version__)

    global guild
    global secrets
    global vipRole
    global beansRole
    global streamerRole
    global welcomeChannel
    global streamerChannel
    global changelogChannel
    global suggestionChannel

    guild = bot.get_guild(601701439995117568)

    # roles
    vipRole         = guild.get_role(601711869668884484)
    streamerRole    = guild.get_role(601710639068610578)
    beansRole       = guild.get_role(601711999939903489)

    # channels
    changelogChannel    = bot.get_channel(603279565439369236)
    welcomeChannel      = bot.get_channel(603284631151706112)
    streamerChannel     = bot.get_channel(604088400819126361)
    suggestionChannel   = bot.get_channel(608371806549704800)

    embed = discord.Embed(title=f"BeanBot v{__version__}", color=0xff6000)
    embed.set_author(name=f"BeanBot Devs", icon_url=bot.user.avatar_url)
    embed.add_field(name="Changelog", value=f"\t- {newline.join(config['meta']['changelog'])}")
    embed.set_footer(text=f"Build #{config['meta']['build_number']}")

    if __version__ != secrets["CACHED_VERSION"] and "--debug" not in argv:
        secrets["CACHED_VERSION"] = __version__
        secrets["CACHED_BUILD"] = config["meta"]["build_number"]
        u.editConfig("secrets.json", secrets)
        secrets = u.reloadConfig("secrets.json")
        
        msg = await changelogChannel.send(embed=embed)
        secrets["CHANGELOG_MESSAGE_ID"] = msg.id

    elif config["meta"]["build_number"] != secrets["CACHED_BUILD"]:
        msg = await changelogChannel.fetch_message(secrets["CHANGELOG_MESSAGE_ID"])
        await msg.edit(embed=embed)
    
    elif "--debug" in argv:
        u.log("Debugging", u.WRN)

    u.log("BeanBot logged in...")
    for extension in initial_extensions:
        bot.load_extension(extension)


@bot.event
async def on_member_join(user: discord.Member):
    await user.add_roles(beansRole)
    await welcomeChannel.send(f"Welcome to the Bean Gang, {user.mention}")


@bot.event
async def on_member_remove(user: discord.Member):
    await welcomeChannel.send(f"The bean gang will miss you, {user.name}")
    await user.send(f"The bean gang will miss you!")
    if twitch.find({"discord_id": str(user.id)}):
        twitch.delete_one({"discord_id": str(user.id)})


@bot.event
async def on_message(message: discord.Message):
    global suggestionChannel

    if message.channel == suggestionChannel:
        embed = discord.Embed(title="New Feature Request!", color=0x8000ff)
        embed.set_author(name=f"{message.author.name}#{message.author.discriminator}", icon_url=message.author.avatar_url)
        embed.add_field(name="Request", value=message.content, inline=True)
        if message.author.id not in config["devs"]:
            await message.author.send("Your request has been sent to the developers. They will respond as soon as possible. The embed below is what they have recieved.", embed=embed)
        u.log(f"Request from {message.author.name}#{message.author.discriminator} recieved...")

        for dev in config["devs"]:
            developer: discord.User = bot.get_user(dev)
            await developer.send(embed=embed)
    await bot.process_commands(message)


async def background_loop():
    await sleep(10)
    await bot.wait_until_ready()

    while not bot.is_closed():
        u.log("Checking twitch...")
        await t.check(streamerChannel)
        await sleep(60)

# dev level commands

@bot.command()
async def reload(ctx):
    u.log(ctx)

    if not u.dev(ctx.author):
        await ctx.send(f"{ctx.author.mention}, only developers can use this command.")
        return

    global config
    config = u.reloadConfig()
    await ctx.send(f"{ctx.author.mention}, reloaded config!")
    return


@bot.command()
async def stop(ctx):
    if not u.dev(ctx.author):
        await ctx.send(f"{ctx.author.mention}, only developers can use this command.")
        return

    u.log("Developer initiated logout...", u.ERR)
    await ctx.send(f"Goodbye...")
    await bot.logout()
    exit(1)

u.log("Starting script...")
bot.loop.create_task(background_loop())
if "--debug" in argv: bot.run(secrets["dev_token"])
else: bot.run(secrets["token"])
