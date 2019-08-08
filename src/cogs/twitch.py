import discord
from discord.ext import commands
from imports.twitch import Twitch

class TwitchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        @commands.command(name="streamer")
        async def streamer(self, ctx, _user: discord.Member = None, _username: str = None):
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
        
            await _user.add_roles(streamerRole)
            twitch.insert_one({
                "twitch_username": _username,
                "message_id": None,
                "discord_id": _user.id,
                "response": {}
            })
            await ctx.send(f"{_user.mention}, {ctx.author.mention} has made you a streamer!")
        
def setup(bot):
    bot.add_cog(TwitchCog(bot))