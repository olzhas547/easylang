from fastapi import APIRouter, HTTPException, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from bson.objectid import ObjectId
from src import users
import models
import datetime
import database
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
router = APIRouter()
templates = Jinja2Templates(directory="templates/")

@router.get('/', response_class=HTMLResponse)
async def test(request: Request):
    return templates.TemplateResponse('test.html', {'request': request})

@router.get('/get_projects')
async def get_projects(request: Request):
    project_names = await users.get_projects()
    projects = []
    for i in project_names:
        project = await users.get_project(i)
        projects.append(project)
    return projects

@router.get('/get_project_names')
async def get_project_names(request: Request):
    project_names = await users.get_projects()
    return project_names

@router.get('/get_activities')
async def get_activities_of_the_project(request: Request, project: str):
    return await users.get_activities_of_the_project(project)

@router.get('/get_list_of_chief_editors')
async def get_list_of_chief_editors(request: Request):
    return await users.get_list_of_chief_editors()

###############################################################################

@router.get("/projects")
async def show_projects(request: Request):
    chief_editors_list = await users.get_list_of_chief_editors()
    user = await users.get_current_user_from_cookie(request)
    if user['role'] == 'project_manager':
        return templates.TemplateResponse('projects.html', {'request': request, 'chief_editors_list': chief_editors_list})
    raise HTTPException(status_code=400, detail='Incorrect user role')
    #return RedirectResponse("http://localhost:8000/")

@router.post("/create_project")
async def create_project(request: Request):
    result = await request.form()
    print(result)
    project_name = result['project_name']
    deadline = result['deadline'].split('-')
    editors = result['editors']
    print(result)
    activity = {
        'activity_name': 'initial_activity',
        'project_name': project_name,
        'translators': None,
        'editors': editors,
        'deadline': datetime.datetime(int(deadline[0]), int(deadline[1]), int(deadline[2]), 0, 0),
        'project_status': 'created',
        'completeness': 0
    }
    approve = await users.create_activity(models.ActivityModel(**activity))
    return approve

@router.get("/project")
async def show_project(request: Request):
    user = await users.get_current_user_from_cookie(request)
    if user['role'] == 'project_manager':
        return templates.TemplateResponse('project.html', {'request': request})
    raise HTTPException(status_code=400, detail='Incorrect user role')
    #return RedirectResponse("http://localhost:8000/")

@router.get("/activity")
async def show_activity(request: Request):
    user = await users.get_current_user_from_cookie(request)
    if user['role'] == 'project_manager':
        return templates.TemplateResponse('activities.html', {'request': request})
    raise HTTPException(status_code=400, detail='Incorrect user role')
    #return RedirectResponse("http://localhost:8000/")
    
@router.get("/chief_editor")
async def show_chief_editor(request: Request):
    user = await users.get_current_user_from_cookie(request)
    if user['role'] == 'project_manager':
        return templates.TemplateResponse('chief_editor.html', {'request': request})
    raise HTTPException(status_code=400, detail='Incorrect user role')
    #return RedirectResponse("http://localhost:8000/")

@router.get("/translator")
async def show_translator(request: Request):
    user = await users.get_current_user_from_cookie(request)
    if user['role'] == 'project_manager':
        return templates.TemplateResponse('translator.html', {'request': request})
    raise HTTPException(status_code=400, detail='Incorrect user role')

###############################################################################

@router.get("/users_list")
async def users_list_in_bd():
    users_list = []
    async for user in database.users_collection.find():
        users_list.append(users.user_helper(user))
    return users_list

@router.get("/tokens")
async def read_tokens():
    tokens = []
    async for token in database.tokens_collection.find():
        tokens.append(users.token_helper(token))
    return tokens

@router.get("/delete_tokens")
async def delete_tokens():
    async for token in database.tokens_collection.find():
        database.tokens_collection.delete_one({"_id": ObjectId(users.token_helper(token)["access_token"])})
    return True

@router.get("/delete")
async def delete_user(id: str):
    user = await database.users_collection.find_one({"_id": ObjectId(id)})
    if user:
        await database.users_collection.delete_one({"_id": ObjectId(id)})
        return True


@router.post("/sign-up", response_model=models.User)
async def app_create_user(user: models.UserCreate):
    db_user = await users.get_user_by_login(login=user.login)
    if db_user:
        raise HTTPException(status_code=400, detail="Login already registered")
    return await users.create_user(user=user)

@router.get('/login', response_class=HTMLResponse)
async def login(request: Request, not_valid: bool = False):
    return templates.TemplateResponse('registration_page.html', {'request': request, 'not_valid': not_valid})

@router.get('/forgot_password', response_class=HTMLResponse)
async def forgot_password(request: Request, not_valid: bool = False):
    return templates.TemplateResponse('forgot_password.html', {'request': request, 'not_valid': not_valid})

@router.post("/login_form")
async def auth(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users.get_user_by_login(login=form_data.username)
    if not user:
        raise HTTPException(status_code=302, detail="Incorrect login or password", headers = {"Location": "http://localhost:8000/login?not_valid=true"})
        
    if not users.validate_password(
        password=form_data.password, hashed_password=user["password"]
    ):
        raise HTTPException(status_code=302, detail="Incorrect login or password", headers = {"Location": "http://localhost:8000/login?not_valid=true"})

    token = await users.create_user_token(user_id=users.user_helper(user)["id"])
    response.set_cookie(
        key=users.COOKIE_NAME,
        value=token,
        httponly=True,
        expires=1800
    )
    response_project_manager = RedirectResponse('http://localhost:8000/projects', status_code=status.HTTP_303_SEE_OTHER)
    response_project_manager.set_cookie(
        key=users.COOKIE_NAME,
        value=token,
        httponly=True,
        expires=1800
    )
    if user['role'] == 'project_manager':
        return response_project_manager
    return token

@router.get("/me", response_model=models.UserBase)
async def read_users_me(request: Request):
    return await users.get_current_user_from_cookie(request)

@router.get("/user/status")
async def get_status(request: Request):
    user = await users.get_current_user_from_cookie(request)
    return await users.get_status(user)

@router.post("/user/status")
async def set_status(user_status: str, current_user: models.User = Depends(users.get_current_user)):
    return await users.set_status(user_status, current_user)

@router.post("/create_activity")
async def create_activity(activity: models.ActivityModel, current_user: models.User = Depends(users.get_current_user)):
    if current_user["role"] != 'project_manager':
        raise HTTPException(status_code=400, detail='Incorrect user role')
    return await users.create_activity(activity)

@router.post("/set_activity_estimated_time")
async def set_activity_estimated_time(activity: str, time: int, current_user: models.User = Depends(users.get_current_user)):
    if current_user["role"] != 'translator':
        raise HTTPException(status_code=400, detail='Incorrect user role')
    return await users.set_time(ObjectId(activity), time)

@router.post("/user/set_activity_translator")
async def set_activity_translator(activity: str, translator_id: str, current_user: models.User = Depends(users.get_current_user)):
    if current_user["role"] != 'project_manager':
        raise HTTPException(status_code=400, detail='Incorrect user role')
    return await users.set_activity_translator(ObjectId(activity), ObjectId(translator_id))

@router.post("/user/set_activity_editor")
async def set_activity_editor(activity: str, editor_id: str, current_user: models.User = Depends(users.get_current_user)):
    if current_user["role"] != 'project_manager':
        raise HTTPException(status_code=400, detail='Incorrect user role')
    return await users.set_activity_editor(ObjectId(activity), ObjectId(editor_id))