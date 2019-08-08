import time
import discord
import requests

from imports.utils import Utils

class Twitch:
    """
    Twitch integration stuff
    """

    config      : dict
    secrets     : dict
    twitch      : dict
    u           : Utils
    bot         : discord.Client

    def __init__(self, config: dict, secrets: dict, twitch: dict, bot: discord.Client):
        """Twitch(config, secrets, twitch)"""
        self.config     = config
        self.secrets    = secrets
        self.twitch     = twitch
        self.u          = Utils(config)
        self.bot        = bot

    async def check(self, streamerChannel: discord.TextChannel):
        for streamer in self.twitch["channels"]:
            self.u.log(f"\tChecking if {streamer} is live...")
            r = requests.get(f"https://api.twitch.tv/helix/streams?user_login={streamer}",
                             headers={"Client-ID": self.secrets["twitchToken"]})
            streamData = r.json()
            r.close()

            if streamData["data"]:
                streamData = r.json()["data"][0]
                r = requests.get(f"https://api.twitch.tv/helix/users?id={streamData['user_id']}",
                                 headers={"Client-ID": self.secrets["twitchToken"]})
                userData = r.json()["data"][0]
                r.close()

                r = requests.get(f"https://api.twitch.tv/helix/games?id={streamData['game_id']}",
                                 headers={"Client-ID": self.secrets["twitchToken"]})
                gameData = r.json()["data"][0]
                r.close()

                name    = streamer
                msgName = streamer
                avatar  = userData["profile_image_url"].format(width=500, height=500)
                if streamer in self.twitch["twitch_links"]: 
                    user    = self.bot.get_user(self.twitch["twitch_links"][streamer])
                    avatar  = user.avatar_url
                    name    = user.name
                    msgName = user.mention

                embed = discord.Embed(title=streamData["title"], url=f"https://twitch.tv/{streamer}", color=0x8000ff)
                embed.set_author(name=name, icon_url=avatar)
                embed.set_thumbnail(url=gameData["box_art_url"].format(width=390, height=519))
                embed.set_image(url=streamData["thumbnail_url"].format(width=1280, height=720))
                embed.add_field(name="Game", value=gameData["name"], inline=True)
                embed.add_field(name="Viewers", value=streamData["viewer_count"], inline=True)
                
                if streamer not in self.twitch["messages"]:
                    self.u.log(f"\t\t{streamer} is now live, announcing stream...")
                    msg = await streamerChannel.send(f"@everyone {msgName} is live!", embed=embed)
                    self.twitch["messages"][streamer] = msg.id
                elif self.twitch["responses"][streamer] != streamData:
                    self.u.log(f"\t\tUpdating {streamer}\'s live message...")
                    msg = await streamerChannel.fetch_message(self.twitch["messages"][streamer])
                    await msg.edit(embed=embed)
                self.twitch["responses"][streamer] = streamData
                self.u.editConfig("twitch.json", self.twitch)
                self.twitch = self.u.reloadConfig("twitch.json")

            else:
                if streamer in self.twitch["messages"]:
                    self.u.log(f"\t\t{streamer} is no longer live, deleting message...")
                    msg = await streamerChannel.fetch_message(self.twitch["messages"][streamer])
                    await msg.delete()
                    del self.twitch["messages"][streamer]
                    del self.twitch["responses"][streamer]
                    self.u.editConfig("twitch.json", self.twitch)
                    self.twitch = self.u.reloadConfig("twitch.json")