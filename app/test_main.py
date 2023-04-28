import pytest
from httpx import AsyncClient
from bson.objectid import ObjectId
from pydantic import ValidationError
import datetime

from app import app
from src import users
import models

@pytest.mark.anyio
async def test_auth_valid_password():
    request_invalid_password = 'username=manager_project&password=manager_project'
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response_not_existing_user = await ac.post(
            "/login_form",
            headers={
                'Content-Type': 'application/x-www-form-urlencoded', 
                'accept': 'application/json'
            }, 
            data=request_invalid_password
        )
    assert response_not_existing_user.status_code == 303

@pytest.mark.anyio
async def test_auth_invalid_login():
    request_invalid_password = 'username=manareg_project&password=manager_project'
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response_not_existing_user = await ac.post(
            "/login_form", 
            headers={
                'Content-Type': 'application/x-www-form-urlencoded', 
                'accept': 'application/json'
            }, 
            data=request_invalid_password)
    assert response_not_existing_user.status_code == 302
    assert response_not_existing_user.json() == {
        'detail': 'Incorrect login or password'
    }

@pytest.mark.anyio
async def test_auth_invalid_password():
    request_invalid_password = 'username=manager_project&password=manareg_project'
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response_not_existing_user = await ac.post(
            "/login_form", 
            headers={
                'Content-Type': 'application/x-www-form-urlencoded', 
                'accept': 'application/json'
            }, 
            data=request_invalid_password
        )
    assert response_not_existing_user.status_code == 302
    assert response_not_existing_user.json() == {
        'detail': 'Incorrect login or password'
    }

def test_get_random_string_len_12():
    result = users.get_random_string(12)
    assert type(result) is str
    assert len(result) == 12

def test_get_random_string_len_not_12():
    result = users.get_random_string(1)
    assert type(result) is str
    assert len(result) == 1

@pytest.mark.anyio
async def test_get_user_by_login():
    result = await users.get_user_by_login('manager_project')
    assert result == {
    '_id': ObjectId("643bf7db29a8f8dcc00a1bd9"),
    'login': 'manager_project',
    'username': 'manager_project',
    'password': 'VgGdZKkexOUy$e1f631580bc78759077f5398a4b4661c846e0f3ddea4ae992b51991fc6ae95d5',
    'role': 'project_manager',
    'status': 'project_manager',
    'efficiency': 0,
    'is_active': True
  }

@pytest.mark.anyio
async def test_get_user_by_invalid_login():
    result = await users.get_user_by_login('manareg_project')
    assert result == None

def test_validate_valid_password():
    result = users.validate_password(
        'manager_project', 
        'VgGdZKkexOUy$e1f631580bc78759077f5398a4b4661c846e0f3ddea4ae992b51991fc6ae95d5'
    )
    assert result == True

def test_validate_invalid_password():
    result = users.validate_password(
        'manareg_project', 
        'VgGdZKkexOUy$e1f631580bc78759077f5398a4b4661c846e0f3ddea4ae992b51991fc6ae95d5'
    )
    assert result == False

@pytest.mark.anyio
async def test_create_user_token():
    result = await users.create_user_token('643bf7db29a8f8dcc00a1bd9')
    assert result['token_type'] == 'bearer'
    assert result['user_id'] == '643bf7db29a8f8dcc00a1bd9'
    assert type(result['access_token']) is str
    assert type(result['expires']) is datetime.datetime

def test_hash_password():
    result = users.hash_password('manager_project')
    assert type(result) is str

def test_user_helper_valid():
    user = {
        '_id': ObjectId("643bf7db29a8f8dcc00a1bd9"),
        'login': 'manager_project',
        'username': 'manager_project',
        'password': 'VgGdZKkexOUy$e1f631580bc78759077f5398a4b4661c846e0f3ddea4ae992b51991fc6ae95d5',
        'role': 'project_manager',
        'status': 'project_manager',
        'efficiency': 0,
        'is_active': True
    }
    assert users.user_helper(user) == {
        'id': '643bf7db29a8f8dcc00a1bd9', 
        'login': 'manager_project', 
        'username': 'manager_project', 
        'password': 'VgGdZKkexOUy$e1f631580bc78759077f5398a4b4661c846e0f3ddea4ae992b51991fc6ae95d5', 
        'role': 'project_manager', 
        'efficiency': 0, 
        'status': 'project_manager', 
        'is_active': True
    }

def test_user_helper_invalid():
    user = {
        '_id': ObjectId("643bf7db29a8f8dcc00a1bd9"),
        'login': 'manager_project',
        'password': 'VgGdZKkexOUy$e1f631580bc78759077f5398a4b4661c846e0f3ddea4ae992b51991fc6ae95d5',
        'role': 'project_manager',
        'status': 'project_manager',
        'efficiency': 0,
        'is_active': True
    }
    with pytest.raises(KeyError):
        users.user_helper(user)

def test_token_helper_valid():
    token = {
        "_id": "643bf9e89d1255fd52d043ce",
        "user_id": '643bf7db29a8f8dcc00a1bd9',
        "expires": "2023-04-30T19:36:40.236Z",
        'token_type': 'bearer'
    }
    assert users.token_helper(token) == {
        'access_token': '643bf9e89d1255fd52d043ce', 
        'expires': '2023-04-30T19:36:40.236Z', 
        'token_type': 'bearer', 
        'user_id': '643bf7db29a8f8dcc00a1bd9'
    }

def test_token_helper_invalid():
    token = {
        "_id": "643bf9e89d1255fd52d043ce",
        "user_id": '643bf7db29a8f8dcc00a1bd9',
        "expires": "2023-04-30T19:36:40.236Z"
    }
    with pytest.raises(KeyError):
        users.user_helper(token)
        





@pytest.mark.anyio
async def test_create_project():
    '''
    WHEN
    Project name IS Test Project 4
    Deadline IS 2023-04-23
    Chief Editor IS Chief Editor 2
    
    THEN
    Project created
    '''
    request_create_project = 'project_name=Test+Project+4&deadline=2023-04-23&editors=Chief+Editor+2'
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response_create_project = await ac.post(
            "/create_project", 
            headers={
                'Content-Type': 'application/x-www-form-urlencoded', 
                'accept': 'application/json'
            }, 
            data=request_create_project
        )
    assert response_create_project.status_code == 303

@pytest.mark.anyio
async def test_create_project_invalid():
    '''
    WHEN
    Project name IS Test Project 4
    Deadline IS 2023-04-23
    
    THEN
    Project not created. Chief editor not found
    '''
    request_create_project_invalid = 'project_name=Test+Project+0&deadline=2023-04-19'
    async with AsyncClient(
        app=app, 
        base_url="http://localhost:8000"
    ) as ac:
        await ac.post(
            "/create_project", 
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'accept': 'application/json'
            }, 
            data=request_create_project_invalid
        )
        

@pytest.mark.anyio
async def test_create_activity():
    activity = {
        'activity_name': 'initial_activity',
        'project_name': 'project_name',
        'translators': None,
        'editors': 'editor',
        'deadline': datetime.datetime(int('2022'), int('08'), int('05'), 0, 0),
        'project_status': 'created',
        'completeness': 0
    }
    result = await users.create_activity(models.ActivityModel(**activity))
    assert type(result) is str

@pytest.mark.anyio
async def test_create_activity_invalid():
    with pytest.raises(ValidationError):
        activity = {
            'activity_name': 'initial_activity',
            'translators': None,
            'editors': 'editor',
            'deadline': datetime.datetime(
                int('2022'), int('08'), int('05'), 0, 0
            ),
            'project_status': 'created',
            'completeness': 0
        }
        await users.create_activity(models.ActivityModel(**activity))

@pytest.mark.anyio
async def test_edit_project():
    '''
    WHEN
    Project name IS Test Project 4
    Deadline IS 2023-05-09
    Chief Editor IS Chief Editor 2
    
    THEN
    Project edited
    '''
    request_edit_project = 'project_name=Test+Project+4&deadline=2023-05-09&editors=Chief+Editor+1&_id=644242b3c18459dc775e14bc'
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response_edit_project = await ac.post(
            "/edit_project", 
            headers={
                'Content-Type': 'application/x-www-form-urlencoded', 
                'accept': 'application/json'
            }, 
            data=request_edit_project
        )
    assert response_edit_project.status_code == 303

@pytest.mark.anyio
async def test_edit_project_invalid():
    '''
    WHEN
    Deadline IS 2023-05-09
    Chief Editor IS Chief Editor 2
    
    THEN
    Project not edited
    '''
    with pytest.raises(KeyError):
        request_edit_project = 'deadline=2023-05-09&editors=Chief+Editor+1&_id=644242b3c18459dc775e14bc'
        async with AsyncClient(
            app=app, 
            base_url="http://localhost:8000"
        ) as ac:
            await ac.post(
                "/edit_project", 
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded', 
                    'accept': 'application/json'
                }, 
                data=request_edit_project
            )

@pytest.mark.anyio
async def test_edit_project_invalid_name():
    '''
    WHEN
    Project name IS Test Project 1
    Deadline IS 2023-05-09
    Chief Editor IS Chief Editor 2
    
    THEN
    Project not edited
    '''
    request_edit_project = 'project_name=Test+Project+4&deadline=2023-05-09&editors=Chief+Editor+1&_id=644242b3c18459dc775e14bc'
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response_edit_project = await ac.post(
            "/edit_project", 
            headers={
                'Content-Type': 'application/x-www-form-urlencoded', 
                'accept': 'application/json'
            }, 
            data=request_edit_project
        )
    assert response_edit_project.status_code == 303
    assert response_edit_project.url == 'http://localhost:8000/edit_project'

@pytest.mark.anyio
async def test_edit_project_invalid_deadline():
    '''
    WHEN
    Project name IS Test Project 1
    Deadline IS 2020-05-09
    Chief Editor IS Chief Editor 2
    
    THEN
    Project not edited
    '''
    request_edit_project = 'project_name=Test+Project+4&deadline=2023-05-09&editors=Chief+Editor+1&_id=644242b3c18459dc775e14bc'
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response_edit_project = await ac.post(
            "/edit_project", 
            headers={
                'Content-Type': 'application/x-www-form-urlencoded', 
                'accept': 'application/json'
            }, 
            data=request_edit_project
        )
    assert response_edit_project.status_code == 303
    assert response_edit_project.url == 'http://localhost:8000/edit_project'

@pytest.mark.anyio
async def test_get_project_names():
    result = await users.get_project_names()
    assert result == ['Test Project 4', 'project_name']