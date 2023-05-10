import motor.motor_asyncio
from os import environ
import asyncio

MONGO_DETAILS = ("mongodb://admin:password123@mongo:27017/fastapi?authSource=admin")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
client.get_io_loop = asyncio.get_event_loop

if environ.get("TESTING"):
    database = client.test
else:
    database = client.users

users_collection = database.get_collection('users_collection')
tokens_collection = database.get_collection('tokens_collection')
activities_collection = database.get_collection('activities_collection')

