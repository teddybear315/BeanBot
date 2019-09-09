import json

from pymongo import MongoClient
from pymongo.collection import Collection

from src.modules.utils import utils

mongo = MongoClient("mongodb://localhost:27017")

cfg = json.load(open("config/config.json"))
utils = utils(cfg)

def twitch():
    return mongo.get_database("BeanBot").get_collection("Streamers")

def u():
    return utils

def config():
    return json.load(open("config/config.json"))

def secrets():
    return json.load(open("config/secrets.json"))
