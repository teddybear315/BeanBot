import json

from pymongo import MongoClient
from pymongo.collection import Collection

from imports.utils import Utils

mongo = MongoClient("mongodb://localhost:27017")
beanbot_db = mongo.get_database("BeanBot")
twitch_db: Collection = beanbot_db.get_collection("Streamers")

cfg = json.load(open("config/config.json"))
scrts = json.load(open("config/secrets.json"))

utils = Utils(cfg)

def twitch():
    return twitch_db

def u():
    return utils

def config():
    return cfg

def secrets():
    return scrts