import time
import json
import discord

from discord.ext.commands import Context
from termcolor import cprint

class Utils:
    """Utilities class"""
    CMD = 1
    WRN = 2
    ERR = 3
    LOG = 4

    def __init__(self, _config):
        """Utils(config)"""
        self.config = _config


    def vip(self, author: discord.Member):
        """Returns if user is a vip"""
        for role in author.roles:
            if role.id == 601711869668884484: return True
        return False

    def streamer(self, user: discord.Member):
        """Returns if a user is a streamer"""
        for role in user.roles:
            if role.id == 601710639068610578: return True
        return False

    def dev(self, author: discord.Member):
        """Returns if user is a developer"""
        if author.id in self.config["devs"]: return True
        return False

    def editConfig(self, fp, value):
        """Edits a config file with a dictionary"""
        json_str = json.dumps(value)
        with open(f"config/{fp}", "w+") as f:
            f.write(json_str)
            f.close()

    def reloadConfig(self, configFP = "config.json"):
        """
        Loads a config file (json formatted) into a variable
        Usage: configFile = reloadConfig(configFile)
        """
        fp = f"config/{configFP}"
        _json = json.dumps(json.load(open(fp)))
        with open(fp, "w+") as f:
            f.write(_json)
            f.close()
        return json.load(open(fp))

    def log(self, msg, lvl = LOG):
        """Decent logging system"""
        logString = f"{time.strftime('%H:%M:%S')}: {msg}"
        if type(msg) is Context:
            logString = f"{time.strftime('%H:%M:%S')}: {msg.command.name} command ran by {msg.author.name}#{msg.author.discriminator}"
            lvl = self.CMD
        if lvl == self.WRN:
            cprint("[WRN] " + logString, color="yellow")
        elif lvl == self.ERR:
            cprint("[ERR] " + logString, color="red")
        elif lvl == self.CMD:
            cprint("[CMD] " + logString, color="green")
        else:
            print("[LOG] " + logString)