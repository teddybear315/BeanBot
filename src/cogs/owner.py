import discord

from discord.ext import commands
from discord.ext.commands import Context

from src.modules import u, config

config = config()
u = u()

class OwnersCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    async def reload(ctx):
        u.log(ctx)

        if not u.dev(ctx.author):
            await ctx.send(f"{ctx.author.mention}, only developers can use this command.")
            return

        global config
        config = u.reloadConfig()
        await ctx.send(f"{ctx.author.mention}, reloaded config!")
        return

    @commands.command()
    async def stop(ctx):
        if not u.dev(ctx.author):
            await ctx.send(f"{ctx.author.mention}, only developers can use this command.")
            return

        u.log("Developer initiated logout...", u.ERR)
        await ctx.send(f"Goodbye...")
        await bot.logout()
        exit(1)

def setup(bot):
    bot.add_cog(OwnersCog(bot))