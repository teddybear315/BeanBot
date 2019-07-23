import time
import json
import discord

from discord.ext.commands import Bot
from discord.ext.commands import Context as Context

# local imports
from imports import sql
from imports.utils import Utils
from imports.utils import vipId


config = json.load(open("..\\config\\config.json"))
settings = sql.create_connection("..\\config\\settings.db")
c = settings.cursor()

bot = Bot(command_prefix=config["bot"]["prefix"],
          case_insensitive=True,
          description=config["bot"]["description"],
          owner_ids=config["devs"],
          activity=discord.Activity(type=discord.ActivityType.playing, name="games with the Bean Gang.")
          )

u = Utils(config)

guild: discord.Guild
vipRole: discord.Role


# Create table
c.execute('''CREATE TABLE IF NOT EXISTS USERS
             (USERNAME text, DISCRIMINATOR integer, ID integer, LEVEL integer)''')


@bot.event
async def on_ready():
    global guild
    global vipRole

    guild = await bot.fetch_guild(601701439995117568)

    # roles
    if type(guild) == discord.Guild:
        vipRole = guild.get_role(601711869668884484)
    else:
        exit()
    print("BeanBot logged in...")


@bot.command()
async def raid(ctx:Context, twitchChannel:str = None):
    await ctx.message.delete()
    if not u.vip(ctx.author):
        msg = await ctx.send(f"{ctx.author.mention}, only VIPs can use this command.")
        time.sleep(3)
        await msg.delete()
        return

    if not twitchChannel:
        msg = await ctx.send(f"{ctx.author.mention}, please specify a channel name.")
        time.sleep(2)
        await msg.delete()
        return
    await ctx.send(f"@   everyone we're raiding https://twitch.tv/{twitchChannel}")

@bot.command(name="vip")
async def _vip(ctx, _user: discord.Member = None):
    await ctx.message.delete()
    if not u.vip(ctx.author):
        msg = await ctx.send(f"{ctx.author.mention}, only VIPs can use this command.")
        time.sleep(3)
        await msg.delete()
        return

    if not _user:
        msg = await ctx.send(f"{ctx.author.mention}, please tag a user to make them a VIP.")
        time.sleep(2)
        await msg.delete()
        return

    if vipRole in _user.roles:
        msg = await ctx.send(f"{ctx.author.mention}, that user is already a VIP.")
        time.sleep(2)
        await msg.delete()
        return

    await _user.add_roles(vipRole)
    await ctx.send(f"{_user.mention}, {ctx.author.mention} has made you a VIP!")


# developer commands

@bot.command(name="dev")
async def _dev(ctx, _user: discord.Member = None):
    await ctx.message.delete()
    if not u.dev(ctx.author):
        msg = await ctx.send(f"{ctx.author.mention}, only developers can use this command.")
        time.sleep(3)
        await msg.delete()
        return

    if not _user:
        msg = await ctx.send(f"{ctx.author.mention}, please tag a user to make them a developer.")
        time.sleep(2)
        await msg.delete()
        return

    global config
    if _user.id in config["devs"]:
        msg = await ctx.send(f"{ctx.author.mention}, that user is already a developer.")
        time.sleep(2)
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
        time.sleep(3)
        await msg.delete()
        return
    if _config.lower() == "config" or _config.lower() == "c":
        global config
        config = u.reloadConfig()
        msg = await ctx.send(f"{ctx.author.mention}, reloaded config!")
        time.sleep(1)
        await msg.delete()
        return
    else:
        global settings
        settings.commit()
        settings.close()
        settings = sql.create_connection("..\\config\\settings.db")
        global c
        c = settings.cursor()
        msg = await ctx.send(f"{ctx.author.mention}, reloaded settings database!")
        time.sleep(1)
        await msg.delete()
        return

@bot.command()
async def stop(ctx):
    await ctx.message.delete()
    if not u.dev(ctx.author):
        msg = await ctx.send(f"{ctx.author.mention}, only developers can use this command.")
        time.sleep(3)
        await msg.delete()
        return
    msg = await ctx.send(f"Goodbye...")
    time.sleep(1)
    await msg.delete()
    await bot.logout()
    settings.commit()
    settings.close()
    exit(1)


if __name__ in "__main__":
    bot.run(config["secrets"]["token"])
    settings.commit()
    settings.close()