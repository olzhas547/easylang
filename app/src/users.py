import hashlib
import random
import string
from fastapi.security import OAuth2PasswordBearer
from fastapi import  Request
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import database
from config import settings
import models
from jose import JWTError, jwt

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "login": str(user["login"]),
        "username": user["username"],
        "password": user["password"],
        "role": user["role"],
        "efficiency": user["efficiency"],
        "status": user["status"],
        "is_active": user["is_active"]
    }

def token_helper(token) -> dict:
    return {
        "access_token": str(token["_id"]),
        "user_id": str(token["user_id"]),
        "expires": token["expires"],
        'token_type': token['token_type']
    }

def project_helper(activity) -> dict:
    return {
        'project_name': activity['project_name'],
        'chief_editor': str(activity['editors']),
        'status': activity['project_status'],
        'deadline': str(activity['deadline'])
    }

def activity_helper(activity) -> dict:
    return {
        'project_name': activity['project_name'],
        'editor': str(activity['editor']),
        'status': 'placeholder',
        'deadline': 'placeholder',
        'activity_name': activity['activity_name'],
        'translator': str(activity['translator']),
        'deadline': activity['deadline'],
        'project_status': activity['project_status'],
        'completeness': activity['completeness']
    }


def get_random_string(length: int=12) -> str:
    return "".join(random.choice(string.ascii_letters) for _ in range(length))

def hash_password(password: str, salt: str = None):
    if salt is None:
        salt = get_random_string()
    enc = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return enc.hex()

def validate_password(password: str, hashed_password: str) -> bool:
    salt, hashed = hashed_password.split("$")
    return hash_password(password, salt) == hashed

async def get_user_by_login(login: str):
    return await database.users_collection.find_one({"login": login})

async def create_user_token(user_id: str):
    token_query = {
        "user_id": user_id,
        "expires": datetime.now() + timedelta(weeks=2),
        'token_type': 'bearer'
    }
    token_result = await database.tokens_collection.insert_one(token_query)
    token_id = token_result.inserted_id
    token = await database.tokens_collection.find_one({"_id": token_id})
    return token_helper(token)

async def create_user(user: models.UserCreate):
    salt = get_random_string()
    hashed_password = hash_password(user.password, salt)
    new_user = {
        "login": user.login,
        "username": user.username,
        "password": f"{salt}${hashed_password}",
        "role": user.role,
        "status": user.status,
        "efficiency": 0.0,
        "is_active": True
    }
    user_id = await database.users_collection.insert_one(new_user)
    token = await create_user_token(str(user_id.inserted_id))
    token_dict = {"access_token": token["access_token"], "expires": token["expires"]}

    return {**user.dict(), "id": user_id, "is_active": True, "token": token_dict}

async def set_status(status, user):
    result = await database.users_collection.update_one({"login": user["login"]}, {"$set" : {"status": status}})
    return result.modified_count

async def get_status(user) -> str:
    result = await database.users_collection.find_one({"login": user["login"]})
    return user_helper(result)["status"]


#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login_form")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
COOKIE_NAME = 'Authorization'


def verify_access_token(token: str, credentials_exception):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception

        token_data = models.TokenData(id=id)

    except JWTError:
        raise credentials_exception

    return token_data

async def get_current_user():
    pass

async def get_current_user_from_cookie(request:Request):
    token=request.cookies.get(COOKIE_NAME)
    if token:
        user = await database.users_collection.find_one({"_id": ObjectId(token[57:81])})
        return user


async def create_activity(activity: models.ActivityModel):
    new_activity = {
        'activity_name': activity.activity_name,
        'project_name': activity.project_name,
        'translators': activity.translators,
        'editors': activity.editors,
        'deadline': activity.deadline,
        'project_status': activity.project_status,
        'completeness': activity.completeness
    }
    activity_id = await database.activities_collection.insert_one(new_activity)
    return str(activity_id.inserted_id)


async def set_time(activity: ObjectId, time: int):
    result = await database.activities_collection.update_one({"_id": activity}, {"$set" : {"time": time}})
    return result.modified_count

async def set_activity_translator(activity: ObjectId, translator_id: ObjectId):
    result = await database.activities_collection.update_one({"_id": activity}, {"$set" : {"translator": translator_id}})
    return result.modified_count

async def set_activity_editor(activity: ObjectId, editor_id: ObjectId):
    result = await database.activities_collection.update_one({"_id": activity}, {"$set" : {"editor": editor_id}})
    return result.modified_count

async def get_projects():
    result = await database.activities_collection.distinct('project_name')
    return result

async def get_project(project_name: str):
    result = await database.activities_collection.find_one({'project_name': project_name})
    return project_helper(result)

async def get_activities():
    result = await database.activities_collection.distinct('activity_name')
    return result

async def get_activity(activity_name: str):
    result = await database.activities_collection.find_one({'activity_name': activity_name})
    return activity_helper(result)

async def get_activities_of_the_project(project: str):
    activities_list = []
    async for activity in database.activities_collection.find({'project_name': project}):
        activities_list.append(activity_helper(activity))
    return activities_list

async def get_list_of_chief_editors():
    chief_editors = []
    async for user in database.users_collection.find({'role': 'chief_editor'}):
        chief_editors.append(user_helper(user)['username'])
    return chief_editors