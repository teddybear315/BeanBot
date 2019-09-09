import json

from pymongo import MongoClient
from pymongo.collection import Collection

from src.modules.utils import Utils

mongo = MongoClient("mongodb://192.168.1.142:27017")
beanbot_db = mongo.get_database("BeanBot")
twitch_db: Collection = beanbot_db.get_collection("Streamers")

config = json.load(open("config/config.json"))
secrets = json.load(open("config/secrets.json"))

utils = Utils(config)