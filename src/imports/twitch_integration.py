import time
import discord
import requests

from imports.utils import Utils
from pymongo.collection import Collection


class Twitch:
    """
    Twitch integration stuff
    """

    config  : dict
    secrets : dict
    twitch  : Collection
    u       : Utils
    bot     : discord.Client

    def __init__(self, config: dict, secrets: dict, twitch: Collection, bot: discord.Client):
        """Twitch(config, secrets, twitch)"""
        self.config = config
        self.secrets = secrets
        self.twitch = twitch
        self.u = Utils(config)
        self.bot = bot

    async def check(self, streamerChannel: discord.TextChannel):
        for streamer in self.twitch.find():
            username = streamer["twitch_username"]

            self.u.log(f"\tChecking if {username} is live...")
            r = requests.get(f"https://api.twitch.tv/helix/streams?user_login={username}", headers={"Client-ID": self.secrets["twitchToken"]})
            streamData = r.json()
            r.close()

            if streamData["data"]:
                streamData = r.json()["data"][0]
                r = requests.get(f"https://api.twitch.tv/helix/users?id={streamData['user_id']}", headers={"Client-ID": self.secrets["twitchToken"]})
                userData = r.json()["data"][0]
                r.close()

                r = requests.get(f"https://api.twitch.tv/helix/games?id={streamData['game_id']}", headers={"Client-ID": self.secrets["twitchToken"]})
                gameData = r.json()["data"][0]
                r.close()

                u.log(int(streamer["discord_id"]))
                user: discord.User  = await self.bot.fetch_user(int(streamer["discord_id"]))
                embed: discord.Embed
                if (streamer["custom_stream_url"]):
                    embed = discord.Embed(title=streamData["title"], url=streamer["custom_stream_url"], color=0x8000ff)
                else:
                    embed = discord.Embed(title=streamData["title"], url=f"https://twitch.tv/{username}", color=0x8000ff)

                embed.set_author(name=user.name, icon_url=user.avatar_url)
                embed.set_thumbnail(url=gameData["box_art_url"].format(width=390, height=519))
                embed.set_image(url=streamData["thumbnail_url"].format(width=1280, height=720))
                embed.add_field(name="Game", value=gameData["name"], inline=True)
                embed.add_field(name="Viewers", value=streamData["viewer_count"], inline=True)

                if not streamer["message_id"]:
                    self.u.log(f"\t\t{username} is now live, announcing stream...")
                    msg = await streamerChannel.send(f"@everyone {user.mention} is live!", embed=embed)
                    streamer["message_id"] = msg.id
                elif streamer["response"] != streamData:
                    self.u.log(f"\t\tUpdating {username}\'s live message...")
                    msg = await streamerChannel.fetch_message(streamer["message_id"])
                    await msg.edit(content=f"@everyone {user.mention} is live!", embed=embed)
                streamer["response"] = streamData

            else:
                if streamer["message_id"]:
                    self.u.log(f"\t\t{username} is no longer live, deleting message...")
                    msg = await streamerChannel.fetch_message(streamer["message_id"])
                    await msg.delete()
                    streamer["response"] = {}
                    streamer["message_id"] = None

            self.twitch.update_one({"twitch_username": username}, {"$set": streamer})
