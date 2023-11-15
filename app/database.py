import motor.motor_asyncio
from os import environ
import asyncio
from config import settings

MONGO_DETAILS = (f'mongodb://{settings.mongo_initdb_root_username}:{settings.mongo_initdb_root_password}@mongo:27017/{settings.mongo_initdb_database}?authSource=admin')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
client.get_io_loop = asyncio.get_event_loop

if environ.get("TESTING"):
    database = client.test
else:
    database = client.users

users_collection = database.get_collection('users_collection')
tokens_collection = database.get_collection('tokens_collection')
activities_collection = database.get_collection('activities_collection')

