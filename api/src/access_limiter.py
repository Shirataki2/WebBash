import datetime
from pymongo import MongoClient


class Limiter:
    def __init__(self):
        self.client = MongoClient('mongodb://mongo:27017')
        self.history = self.client.ip
