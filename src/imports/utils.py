import discord
import json

vipId = 601711869668884484

class Utils:
    """
    Utilities class
    """
    config:dict = {}

    def __init__(self, _config):
        """Utils(config)"""
        self.config = _config


    def vip(self, author: discord.Member):
        """Returns if user is a vip"""
        for role in author.roles:
            if role.id == vipId: return True
        return False


    def dev(self, author: discord.Member):
        """Returns if user is a developer"""
        if author.id in self.config["devs"]: return True
        return False

    def editConfig(self, value):
        json_str = json.dumps(value)
        with open("..\\config\\config.json", "w+") as f:
            f.write(json_str)
            f.close()

    def reloadConfig(self):
        _json = json.dumps(self.config)
        with open("..\\config\\config.json", "w+") as f:
            f.write(_json)
            f.close()

        return json.load(open("..\\config\\config.json"))