import discord

from discord.ext import commands
from discord.ext.commands import Context

from src.modules import utils as u
from src.modules import twitch_db


class Twitch(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot          = bot
        self.guild: discord.Guild       = self.bot.get_guild(601701439995117568)
        self.streamerRole: discord.Role = self.guild.get_role(601710639068610578)


    @commands.command(name="streamer")
    async def streamer(self, ctx, _user: discord.Member = None, _username: str = None):
        u.log(ctx)
        if not u.vip(ctx.author):
            await ctx.send(f"{ctx.author.mention}, only VIPs can use this command.")
            return
        if not _user:
            await ctx.send(f"{ctx.author.mention}, please tag a user to make them a streamer.")
            return
        if not _username:
            await ctx.send(f"{ctx.author.mention}, please specify the users Twitch username.")
            return
        if u.streamer(_user) or twitch_db.find_one({"discord_id": str(_user.id)}):
            await ctx.send(f"{ctx.author.mention}, that user is already a streamer.")
            return

        await _user.add_roles(self.streamerRole)
        twitch_db.insert_one({
            "twitch_username": _username,
            "message_id": None,
            "discord_id": str(_user.id),
            "response": {},
            "custom_stream_url": None
        })
        await ctx.send(f"{_user.mention}, {ctx.author.mention} has made you a streamer!")


    @commands.command()
    async def raid(self, ctx: Context, twitchChannel: str = None):
        u.log(ctx)
        if not u.vip(ctx.author):
            await ctx.send(f"{ctx.author.mention}, only VIPs can use this command.")
            return
        if not twitchChannel:
            await ctx.send(f"{ctx.author.mention}, please specify a channel name.")
            return
        await ctx.send(f"@everyone we're raiding https://twitch.tv/{twitchChannel}")


    @commands.command()
    async def link(self, ctx, url: str = None):
        u.log(ctx)
        if not u.streamer(ctx.author):
            await ctx.send(f"{ctx.author.mention}, only streamers can use this command.")
            return
        if not url:
            await ctx.send(f"{ctx.author.mention}, please enter your custom stream link.")
            return

        if not url.startswith("https://") or not url.startswith("http://"):
            url = "https://" + url

        current_user = twitch_db.find_one({"discord_id": str(ctx.author.id)})
        current_user["custom_stream_url"] = url
        param = {"discord_id": str(ctx.author.id)}
        param2= {"$set": current_user}
        twitch_db.update_one(param, param2)
        await ctx.send(f"{ctx.author.mention}, your custom link has been set!")

def setup(bot):
    bot.add_cog(Twitch(bot))