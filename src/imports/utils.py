import time
import json
import discord

from termcolor import cprint

vipId = 601711869668884484
streamerId = 601710639068610578

class Utils:
    """
    Utilities class
    """
    config:dict = {}
    LOG = 1
    WRN = 2
    ERR = 3

    def __init__(self, _config):
        """Utils(config)"""
        self.config = _config


    def vip(self, author: discord.Member):
        """Returns if user is a vip"""
        for role in author.roles:
            if role.id == vipId: return True
        return False

    def streamer(self, user: discord.Member):
        for role in user.roles:
            if role.id == streamerId: return True
        return False


    def dev(self, author: discord.Member):
        """Returns if user is a developer"""
        if author.id in self.config["devs"]: return True
        return False

    def editConfig(self, fp, value):
        json_str = json.dumps(value)
        with open(f"config/{fp}", "w+") as f:
            f.write(json_str)
            f.close()

    def reloadConfig(self, configFP = "config.json"):
        fp = f"config/{configFP}"
        _json = json.dumps(json.load(open(fp)))
        with open(fp, "w+") as f:
            f.write(_json)
            f.close()
        return json.load(open(fp))

    def log(self, msg, lvl = LOG):
        logString = f"{time.strftime('%H:%M:%S')}: {msg}"
        if lvl == self.LOG:
            print("[LOG] " + logString)
        elif lvl == self.WRN:
            cprint("[WRN] " + logString, color="yellow")
        elif lvl == self.ERR:
            cprint("[ERR] " + logString, color="red")