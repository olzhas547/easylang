import hashlib
import random
import string
from fastapi import  Request
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import database
import models

def user_helper(user) -> dict: #TESTED
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

def token_helper(token) -> dict: #TESTED
    return {
        "access_token": str(token["_id"]),
        "user_id": str(token["user_id"]),
        "expires": token["expires"],
        'token_type': token['token_type']
    }

def project_helper(activity) -> dict: #TESTED
    return {
        'project_name': activity['project_name'],
        'editor': str(activity['editor']),
        'status': activity['project_status'],
        'deadline': str(activity['deadline']),
        'id': str(activity['_id'])
    }

def activity_helper(activity) -> dict: #TESTED
    return {
        '_id': str(activity['_id']),
        'project_name': activity['project_name'],
        'editor': str(activity['editor']),
        'status': activity['status'],
        'activity_name': activity['activity_name'],
        'translator': str(activity['translators']),
        'deadline': activity['deadline'],
        'project_status': activity['project_status'],
        'completeness': activity['completeness']
    }


def get_random_string(length: int=12) -> str: #TESTED
    return "".join(random.choice(string.ascii_letters) for _ in range(length))

def hash_password(password: str, salt: str = None): #TESTED
    if salt is None:
        salt = get_random_string()
    enc = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(), 
        salt.encode(), 
        100_000
    )
    return enc.hex()

def validate_password(password: str, hashed_password: str) -> bool: #TESTED
    salt, hashed = hashed_password.split("$")
    return hash_password(password, salt) == hashed

async def get_user_by_login(login: str): #TESTED
    return await database.users_collection.find_one({"login": login})

async def create_user_token(user_id: str): #TESTED
    token_query = {
        "user_id": user_id,
        "expires": datetime.now() + timedelta(weeks=2),
        'token_type': 'bearer'
    }
    token_result = await database.tokens_collection.insert_one(token_query)
    token_id = token_result.inserted_id
    token = await database.tokens_collection.find_one({"_id": token_id})
    return token_helper(token)

async def create_user(user: models.UserCreate): #TESTED
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
    token_dict = {
        "access_token": token["access_token"],
        "expires": token["expires"]
    }

    return {
        **user.dict(),
        "id": user_id,
        "is_active": True,
        "token": token_dict
    }


async def get_current_user_from_cookie(request:Request):
    token=request.cookies.get('Authorization')
    if token:
        user = await database.users_collection.find_one(
            {"_id": ObjectId(token[57:81])}
        )
        return user


async def create_activity(activity: models.ActivityModel): #TESTED
    new_activity = {
        'activity_name': activity.activity_name,
        'project_name': activity.project_name,
        'translators': activity.translators,
        'editor': activity.editor,
        'deadline': activity.deadline,
        'project_status': activity.project_status,
        'completeness': activity.completeness,
        'status': activity.status
    }
    activity_id = await database.activities_collection.insert_one(new_activity)
    return str(activity_id.inserted_id)


async def edit_project(activity: models.ActivityModel, activity_id: str): #TESTED
    result = await database.activities_collection.update_one(
        {"_id": ObjectId(activity_id)},
        {"$set" : 
            {
                'project_name': activity.project_name,
                'deadline': activity.deadline, 
                'editor': activity.editor
            }
        }
    )
    return result.modified_count

async def edit_activity(activity: models.ActivityModel, activity_id: str): #TESTED
    result = await database.activities_collection.update_one(
        {"_id": ObjectId(activity_id)},
        {"$set" : 
            {
                'activity_name': activity.activity_name,
                'deadline': activity.deadline, 
                'translators': activity.translators
            }
        }
    )
    return result.modified_count

async def get_projects(status: str): #TESTED
    projects = []
    async for project in database.activities_collection.find({
        'activity_name': 'initial_activity', 'project_status': status}
    ):
        projects.append(project_helper(project))
    return projects

async def get_project_by_id(project_id: str): #TESTED
    result = await database.activities_collection.find_one(
        {'_id': ObjectId(project_id)}
    )
    return project_helper(result)


async def get_current_user(): #TESTED
    pass

async def get_project_names(): #TESTED
    result = await database.activities_collection.distinct('project_name')
    return result

async def get_activities_of_the_project(project: str): #TESTED
    activities_list = []
    async for activity in database.activities_collection.find(
        {'project_name': project}
    ):
        activities_list.append(activity_helper(activity))
    return activities_list

async def get_list_of_users(role: str): #TESTED
    users = []
    async for user in database.users_collection.find({'role': role}):
        users.append(
            {
                'username': user_helper(user)['username'],
                'id': user_helper(user)['id']
            }
        )
    return users

async def get_user_by_id(user_id: str): #TESTED
    result = await database.users_collection.find_one(
        {'_id': ObjectId(user_id)}
    )
    return user_helper(result)

async def get_user_activities(user_id: str, user_role: str): #TESTED
    activities_list = []
    async for activity in database.activities_collection.find(
        {user_role: user_id}
    ):
        activities_list.append(activity_helper(activity))
    return activities_list