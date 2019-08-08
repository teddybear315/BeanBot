import time
import json
import discord
import requests

from sys import argv
from asyncio import sleep
from discord.ext.commands import Bot, Context
from discord import Embed

# local imports
from imports.twitch import Twitch
from imports.utils import Utils, vipId

config      = json.load(open("config/config.json"))
twitch      = json.load(open("config/twitch.json"))
secrets     = json.load(open("config/secrets.json"))

__version__ = config["meta"]["version"]
__name__    = "Bean Bot"
__package__ = "Main"
__authors__ = ["Yung Granny#7728", "Luke#1000"]

bot = Bot(command_prefix=config["bot"]["prefix"],
          case_insensitive=True,
          description=config["bot"]["description"],
          owner_ids=config["devs"],
          activity=discord.Activity(type=discord.ActivityType.playing, name="games with the Bean Gang.")
)

u = Utils(config)
t = Twitch(config, secrets, twitch, bot)

guild: discord.Guild

# roles
vipRole         : discord.Role
streamerRole    : discord.Role
beansRole       : discord.Role

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
    vipRole         = guild.get_role(vipId)
    streamerRole    = guild.get_role(601710639068610578)
    beansRole       = guild.get_role(601711999939903489)

    # channels
    changelogChannel    = bot.get_channel(603279565439369236)
    welcomeChannel      = bot.get_channel(603284631151706112)
    streamerChannel     = bot.get_channel(604088400819126361)
    suggestionChannel   = bot.get_channel(608371806549704800)


    if __version__ != secrets["CACHED_VERSION"] and "--debug" not in argv:
        await changelogChannel.send(f"""
***BeanBot v{__version__} online!***
Recent Changes:
\t- {newline.join(config['meta']['changelog'])}
        """)
        secrets["CACHED_VERSION"] = __version__
        u.editConfig("secrets.json", secrets)
        secrets = u.reloadConfig("secrets.json")
    else:
        u.log("Either debugging or couldn\'t find cached version", u.WRN)

    u.log("BeanBot logged in...")


@bot.event
async def on_member_join(user: discord.Member):
    await user.add_roles(beansRole)

    await welcomeChannel.send(f"Welcome to the Bean Gang, {user.mention}")


@bot.event
async def on_member_remove(user: discord.Member):
    await welcomeChannel.send(f"The bean gang will miss you, {user.display_name}")
    await user.send(f"The bean gang will miss you!", tts=True)

@bot.event
async def on_message(message: discord.Message):
    global suggestionChannel
    
    if message.channel == suggestionChannel:
        embed = discord.Embed(title="New Feature Request!", color=0x8000ff)
        embed.set_author(name=f"{message.author.name}#{message.author.discriminator}",
                         icon_url=message.author.avatar_url)
        embed.add_field(name="Request", value=message.content, inline=True)
        await message.author.send("Your request has been sent to the developers. They will respond as soon as possible. The embed below is what they have recieved.",
                                  embed=embed)
        u.log(f"Request from {message.author.name}#{message.author.discriminator} recieved..")
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


@bot.command()
async def raid(ctx:Context, twitchChannel:str = None):
    u.log(ctx)
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

## SET ANY TYPE OF INTERNAL VARIABLE

@bot.command(name="vip")
async def _vip(ctx, _user: discord.Member = None):
    u.log(ctx)
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
async def streamer(ctx, _user: discord.Member = None, _username: str = None):
    u.log(ctx)
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

    global twitch
    await _user.add_roles(streamerRole)
    twitch["channels"].append(_username)
    u.editConfig("twitch.json", twitch)
    twitch = u.reloadConfig("twitch.json")
    await ctx.send(f"{_user.mention}, {ctx.author.mention} has made you a streamer!")

@bot.command()
async def link(ctx, _user: str = None):
    u.log(ctx)
    await ctx.message.delete()
    global twitch
    if not u.streamer(ctx.author) or _user not in twitch["channels"]:
        msg = await ctx.send(f"{ctx.author.mention}, only streamers can use this command.\nIf you are a streamer please contact a VIP or developer.")
        await sleep(3)
        await msg.delete()
        return
    if not _user:
        msg = await ctx.send(f"{ctx.author.mention}, please enter a twitch username.")
        await sleep(3)
        await msg.delete()
        return

    twitch["twitch_links"][_user] = ctx.author.id
    twitch["discord_links"][str(ctx.author.id)] = _user 
    u.editConfig("twitch.json", twitch)
    twitch = u.reloadConfig("twitch.json")
    await ctx.send(f"{ctx.author.mention}, you have linked your Twitch account ({_user}) to your profile!\nThis will grant you a better expierience with our Twitch integration.")

@bot.command()
async def unlink(ctx):
    u.log(ctx)
    await ctx.message.delete()
    global twitch
    if not u.streamer(ctx.author):
        msg = await ctx.send(f"{ctx.author.mention}, only streamers can use this command.\nIf you are a streamer please contact a VIP or developer.")
        await sleep(3)
        await msg.delete()
        return
    if not twitch["discord_links"][str(ctx.author.id)]:
        msg = await ctx.send(f"{ctx.author.mention}, your accounts are not linked.")
        await sleep(3)
        await msg.delete()
        return

    _user = twitch["discord_links"][str(ctx.author.id)]
    del twitch["discord_links"][str(ctx.author.id)]
    del twitch["twitch_links"][_user]
    u.editConfig("twitch.json", twitch)
    twitch = u.reloadConfig("twitch.json")
    await ctx.send(f"{ctx.author.mention}, you have unlinked your Twitch account ({_user})")
    
@bot.command(name="dev")
async def dev(ctx, _user: discord.Member = None):
    u.log(ctx)
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
    u.updateConfig("config.json", config)
    config = u.reloadConfig()
    await ctx.send(f"{_user.mention}, {ctx.author.mention} has made you a developer!")

## END SET ANY TYPE OF INTERNAL VARIABLE

# streamer level command

@bot.command()
async def offline(ctx):
    u.log(ctx)
    await ctx.message.delete()
    global twitch
    if not u.streamer(ctx.author):
        msg = await ctx.send(f"{ctx.author.mention}, only streamers can use this command.")
        await sleep(3)
        await msg.delete()
        return
    if str(ctx.author.id) not in twitch["discord_links"]:
        msg = await ctx.send(f"{ctx.author.mention}, please link your Twitch account to your profile through BeanBot using \`b!link\`.")
        await sleep(3)
        await msg.delete()
        return

    for link in twitch["discord_links"]:
        if int(link) == ctx.author.id:
            streamer = twitch["discord_links"][link]
            del twitch["responses"][streamer]
            msg = await streamerChannel.fetch_message(twitch["messages"][streamer])
            await msg.delete()
            del twitch["messages"][streamer]
    u.updateConfig("twitch.json", twitch)
    twitch = u.reloadConfig("twitch.json")


# dev level commands

@bot.command()
async def reload(ctx):
    u.log(ctx)
    await ctx.message.delete()
    if not u.dev(ctx.author):
        msg = await ctx.send(f"{ctx.author.mention}, only developers can use this command.")
        await sleep(3)
        await msg.delete()
        return

    global config
    config = u.reloadConfig()
    msg = await ctx.send(f"{ctx.author.mention}, reloaded config!")
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
    u.log("Developer initiated logout...", u.ERR)
    msg = await ctx.send(f"Goodbye...")
    await sleep(1)
    await msg.delete()
    await bot.logout()
    exit(1)

u.log("Starting script...")
bot.loop.create_task(background_loop())
bot.run(secrets["token"])