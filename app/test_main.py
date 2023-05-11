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
    request_invalid_password = 'username=test&password=test'
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
    request_invalid_password = 'username=test&password=notest'
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
    result = await users.get_user_by_login('test')
    assert result == {
    '_id': ObjectId('645a485f74b6688020457c41'),
    'login': 'test',
    'username': 'test',
    'password': 'KyyheazmpJDO$aa597210ffc2b5eaff0d45d6de887378b7b34dd36b1e50f35a45dcac071d0da7',
    'role': 'test',
    'status': 'test',
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

def test_project_helper_valid():
    project = {
        'project_name': 'Test',
        'editor': '643bf7db29a8f8dcc00a1bd9',
        'project_status': 'finished',
        'deadline': "2023-04-30T19:36:40.236Z",
        '_id': '643bf7db29a8f8dcc00a1bd9'
    }
    assert users.project_helper(project) == {
        'project_name': 'Test', 
        'editor': '643bf7db29a8f8dcc00a1bd9', 
        'status': 'finished', 
        'deadline': '2023-04-30T19:36:40.236Z', 
        'id': '643bf7db29a8f8dcc00a1bd9'
    }

def test_project_helper_invalid():
    project = {
        'editor': '643bf7db29a8f8dcc00a1bd9',
        'project_status': 'finished',
        'deadline': "2023-04-30T19:36:40.236Z",
        '_id': '643bf7db29a8f8dcc00a1bd9'
    }
    with pytest.raises(KeyError):
        users.user_helper(project)

def test_activity_helper_valid():
    activity = {
        '_id': '643bf7db29a8f8dcc00a1bd9',
        'project_name': 'test',
        'editor': '643bf7db29a8f8dcc00a1bd9',
        'status': 'in_work',
        'activity_name': 'test',
        'translators': '643bf7db29a8f8dcc00a1bd9',
        'deadline': '2023-04-30T19:36:40.236Z',
        'project_status': 'finished',
        'completeness': 0
    }
    assert users.activity_helper(activity) == {
        '_id': '643bf7db29a8f8dcc00a1bd9',
        'project_name': 'test',
        'editor': '643bf7db29a8f8dcc00a1bd9', 
        'status': 'in_work',
        'activity_name': 'test',
        'translator': '643bf7db29a8f8dcc00a1bd9',
        'deadline': '2023-04-30T19:36:40.236Z', 
        'project_status': 'finished', 
        'completeness': 0
    }

def test_activity_helper_invalid():
    activity = {
        'project_name': 'test',
        'editor': '643bf7db29a8f8dcc00a1bd9',
        'status': 'in_work',
        'activity_name': 'test',
        'translators': '643bf7db29a8f8dcc00a1bd9',
        'deadline': '2023-04-30T19:36:40.236Z',
        'project_status': 'finished',
        'completeness': 0
    }
    with pytest.raises(KeyError):
        users.user_helper(activity)

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
    Project name IS "random name"
    Deadline IS 2023-04-23
    Chief Editor IS Chief Editor 2
    
    THEN
    Project created
    '''
    request_create_project = f'project_name={str(ObjectId())}&deadline=2023-04-23&editors=645a4bca08eca36c3778e6a0'
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
        'project_name': str(ObjectId()),
        'translators': None,
        'editor': '645a4bca08eca36c3778e6a0',
        'deadline': datetime.datetime(int('2022'), int('08'), int('05'), 0, 0),
        'project_status': 'created',
        'completeness': 0,
        'status': 'initialized'
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
    Project name IS test
    Deadline IS 2023-05-09
    Chief Editor IS Chief Editor 2
    
    THEN
    Project edited
    '''
    request_edit_project = 'project_name=test&deadline=2023-05-31&_id=645a5064728af5c5703f5aeb&editor=645a4bca08eca36c3778e6a0'
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
        request_edit_project = 'deadline=2023-05-31&_id=645a5064728af5c5703f5aeb&editor=645a4bca08eca36c3778e6a0'
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
    request_edit_project = 'project_name=test&deadline=2023-05-09&editor=645a4bca08eca36c3778e6a0&_id=644242b3c18459dc775e14bc'
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
    request_edit_project = 'project_name=Test+Project+4&deadline=2023-05-09&editor=645a4bca08eca36c3778e6a0&_id=644242b3c18459dc775e14bc'
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
    assert 'test' in result


@pytest.mark.anyio
async def test_change_chief_editor():
    '''
    WHEN
    Chief Editor's id IS 645a4bca08eca36c3778e6a0
    
    THEN
    Project edited
    '''
    request_change_chief_editor = '_id=645a5064728af5c5703f5aeb&editor=645a4bca08eca36c3778e6a0'
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response_change_chief_editor = await ac.post(
            "/project/change_chief_editor", 
            headers={
                'Content-Type': 'application/x-www-form-urlencoded', 
                'accept': 'application/json'
            }, 
            data=request_change_chief_editor
        )
    assert response_change_chief_editor.status_code == 303
    assert response_change_chief_editor.url == 'http://localhost:8000/project/change_chief_editor'
    
@pytest.mark.anyio
async def test_get_user_activities():
    result = await users.get_user_activities("645a4bca08eca36c3778e6a0", 'chief_editor')
    assert type(result) == type([])

@pytest.mark.anyio
async def test_get_activities_of_the_project():
    result = await users.get_activities_of_the_project('test')
    assert type(result) == type([])

@pytest.mark.anyio
async def test_get_current_user():
    result = await users.get_current_user()
    assert result is None

@pytest.mark.anyio
async def test_get_list_of_users_translator():
    result = await users.get_list_of_users('translator')
    assert type(result) == type([])

@pytest.mark.anyio
async def test_get_list_of_users_chief_editor():
    result = await users.get_list_of_users('chief_editor')
    assert type(result) == type([])

@pytest.mark.anyio
async def test_get_list_of_users_project_manager():
    result = await users.get_list_of_users('project_manager')
    assert type(result) == type([])

@pytest.mark.anyio
async def test_get_list_of_users_invalid():
    result = await users.get_list_of_users('project_manareg')
    assert result == []

@pytest.mark.anyio
async def test_get_project_by_id_valid():
    result = await users.get_project_by_id('645a5064728af5c5703f5aeb')
    assert result == {
        'project_name': 'test', 
        'editor': '645a4bca08eca36c3778e6a0', 
        'status': 'created', 
        'deadline': '2023-05-31 00:00:00', 
        'id': '645a5064728af5c5703f5aeb'
    }

@pytest.mark.anyio
async def test_get_project_by_id_invalid():
    with pytest.raises(TypeError):
        await users.get_project_by_id('aaaaaaaaaaaaaaaaaaaaaaaa')

@pytest.mark.anyio
async def test_get_user_by_id_invalid():
    with pytest.raises(TypeError):
        await users.get_user_by_id('aaaaaaaaaaaaaaaaaaaaaaaa')

@pytest.mark.anyio
async def test_get_user_by_id_valid():
    result = await users.get_user_by_id('645a485f74b6688020457c41')
    print(result)
    assert result == {
        'id': '645a485f74b6688020457c41', 
        'login': 'test', 
        'username': 'test', 
        'password': 'KyyheazmpJDO$aa597210ffc2b5eaff0d45d6de887378b7b34dd36b1e50f35a45dcac071d0da7', 
        'role': 'test', 
        'efficiency': 0.0, 
        'status': 'test', 
        'is_active': True
    }

@pytest.mark.anyio
async def test_create_user_valid():
    user = {
        'login': 'abcb',
        'username': 'abcb',
        'password': 'abcb',
        'role': 'translator',
        'status': 'active',
        'efficiency': 0.0,
        'is_active': True,
    }
    result = await users.create_user(models.UserCreate(**user))
    result_filtered = {
        'login': result['login'],
        'username': result['username'], 
        'password': result['password'], 
        'role': result['role'], 
        'status': result['status'], 
        'efficiency': result['efficiency'], 
        'is_active': result['is_active'], 
    }
    assert result_filtered == {
        'login': 'abcb', 
        'username': 'abcb', 
        'password': 'abcb', 
        'role': 'translator', 
        'status': 'active', 
        'efficiency': 0.0, 
        'is_active': True, 
    }

@pytest.mark.anyio
async def test_create_user_invalid():
    user = {
        'username': 'abcb',
        'password': 'abcb',
        'role': 'translator',
        'status': 'active',
        'efficiency': 0.0,
        'is_active': True,
    }
    with pytest.raises(ValidationError):
        await users.create_user(models.UserCreate(**user))

@pytest.mark.anyio
async def test_get_projects_finished():
    result = await users.get_projects('finished')
    print(result)
    assert result == [
        {
            'project_name': '645c90164496e85f3d4aa29f', 
            'editor': '645a4bca08eca36c3778e6a0', 
            'status': 'finished', 
            'deadline': '2022-08-05 00:00:00', 
            'id': '645c90164496e85f3d4aa2a0'
        }
    ]


@pytest.mark.anyio
async def test_get_projects_created():
    result = await users.get_projects('created')
    assert type(result) == type([])

@pytest.mark.anyio
async def test_get_projects_invalid():
    result = await users.get_projects('random')
    assert result == []

@pytest.mark.anyio
async def test_edit_activity_valid():
    activity = {
        'activity_name': 'Random',
        'project_name': '645c90abc6520459d2080bb1',
        'translators': '645c90abc6520459d2080bb1',
        'editor': '645a4bca08eca36c3778e6a0',
        'deadline': datetime.datetime.now(),
        'project_status': 'in work',
        'completeness': 0.0,
        'status': 'created',
    }
    result = await users.edit_activity(
        models.ActivityModel(**activity), 
        '645c90abc6520459d2080bb2'
    )
    assert result == 1

@pytest.mark.anyio
async def test_edit_activity_invalid():
    activity = {
        'activity_name': 'Random',
        'project_name': '645c90abc6520459d2080bb1',
        'translators': '645c90abc6520459d2080bb1',
        'editor': '645a4bca08eca36c3778e6a0',
        'project_status': 'in work',
        'completeness': 0.0,
        'status': 'created',
    }
    with pytest.raises(ValidationError):
        await users.edit_activity(
            models.ActivityModel(**activity), 
            '645c90abc6520459d2080bb2'
        )

@pytest.mark.anyio
async def test_edit_project_valid():
    activity = {
        'activity_name': 'initial_activity',
        'project_name': 'Random',
        'translators': '645c90abc6520459d2080bb1',
        'editor': '645a4bca08eca36c3778e6a0',
        'deadline': datetime.datetime.now(),
        'project_status': 'in work',
        'completeness': 0.0,
        'status': 'created',
    }
    result = await users.edit_activity(
        models.ActivityModel(**activity), 
        '645a52f2cdbdcc9aac282c0e'
    )
    assert result == 1

@pytest.mark.anyio
async def test_edit_project_invalid_unit():
    activity = {
        'activity_name': 'initial_activity',
        'project_name': 'Random',
        'translators': '645c90abc6520459d2080bb1',
        'editor': '645a4bca08eca36c3778e6a0',
        'deadline': datetime.datetime.now(),
        'project_status': 'in work',
        'status': 'created',
    }
    with pytest.raises(ValidationError):
        await users.edit_activity(
            models.ActivityModel(**activity), 
            '645c90abc6520459d2080bb2'
        )

@pytest.mark.anyio
async def test_create_activity_qa():
    '''
    WHEN
    Activity name IS Tesst
    Deadline IS 2023-05-31
    Translator IS abcb
    
    THEN
    Activity created
    '''
    request_create_activity = 'activity_name=Tesst&project_name=645a5252a125ff04c2a26123&current_chief_editor=645a4bca08eca36c3778e6a0&project_id=645a5252a125ff04c2a26124&deadline=2023-05-31&translator=645caf84fc7d556776d73dbb'
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response_create_activity = await ac.post(
            "/project/create_activity", 
            headers={
                'Content-Type': 'application/x-www-form-urlencoded', 
                'accept': 'application/json'
            }, 
            data=request_create_activity
        )
    assert response_create_activity.status_code == 303

@pytest.mark.anyio
async def test_create_activity_qa_invalid():
    '''
    WHEN
    Activity name IS Tesst
    Deadline IS 2023-05-31
    
    THEN
    Activity not created
    '''
    request_create_activity = 'activity_name=Tesst&project_name=645a5252a125ff04c2a26123&current_chief_editor=645a4bca08eca36c3778e6a0&project_id=645a5252a125ff04c2a26124&deadline=2023-05-31'
    with pytest.raises(KeyError):
        async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
            await ac.post(
                "/project/create_activity", 
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded', 
                    'accept': 'application/json'
                }, 
                data=request_create_activity
            )

@pytest.mark.anyio
async def test_edit_activity_qa():
    '''
    WHEN
    Activity name IS Tesst
    Deadline IS 2023-05-31
    Translator IS abcb
    
    THEN
    Activity edited
    '''
    request_create_activity = 'activity_id=645a521df25b7b22ce3e4866&activity_name=Tesst&project_name=645a5252a125ff04c2a26123&current_chief_editor=645a4bca08eca36c3778e6a0&project_id=645a5252a125ff04c2a26124&deadline=2023-05-31&translator=645caf84fc7d556776d73dbb'
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        response_create_activity = await ac.post(
            "/project/edit_activity", 
            headers={
                'Content-Type': 'application/x-www-form-urlencoded', 
                'accept': 'application/json'
            }, 
            data=request_create_activity
        )
    assert response_create_activity.status_code == 303

@pytest.mark.anyio
async def test_edit_activity_qa_invalid():
    '''
    WHEN
    Activity name IS Tesst
    Deadline IS 2023-05-31
    
    THEN
    Activity edited
    '''
    request_create_activity = 'activity_id=645a521df25b7b22ce3e4866&activity_name=Tesst&project_name=645a5252a125ff04c2a26123&current_chief_editor=645a4bca08eca36c3778e6a0&project_id=645a5252a125ff04c2a26124&deadline=2023-05-31'
    with pytest.raises(KeyError):
        async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
            await ac.post(
                "/project/edit_activity", 
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded', 
                    'accept': 'application/json'
                }, 
                data=request_create_activity
            )