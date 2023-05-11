from fastapi import (
    APIRouter, HTTPException, Depends, Request, Response, status
)
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from src import users
import math
import models
import datetime
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()
templates = Jinja2Templates(directory="templates/")
url = "localhost:8000"

@router.get('/', response_class=HTMLResponse)
async def test(request: Request):
    user = await users.get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse(
            f'http://{url}/login', status_code=status.HTTP_303_SEE_OTHER
        )
    if user['role'] == 'project_manager':
        return RedirectResponse(
            f'http://{url}/projects', status_code=status.HTTP_303_SEE_OTHER
        )
    else:
        return RedirectResponse(
            f'http://{url}/me', status_code=status.HTTP_303_SEE_OTHER
        )
    return templates.TemplateResponse('test.html', {'request': request})

@router.get("/projects")
async def show_projects(
        request: Request, archive: bool = False, page: int = 1,
        incorrect_name: bool = False, incorrect_time: bool = False,
    ):
    
    chief_editors_list = await users.get_list_of_users('chief_editor')
    translators_list = await users.get_list_of_users('translator')
    if archive:
        projects = await users.get_projects('finished')
    else:
        projects = await users.get_projects('created')
    projects = sorted(projects, key=lambda d: d['deadline'])
    for project in projects:
        result = await users.get_user_by_id(project['editor'])
        project['editor'] = result['username']
    projects_current_page = projects[8*(page-1):8*page]
    num_of_pages = [x+1 for x in range(math.floor(len(projects)/8) + 1)]
    user = await users.get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse(
            f'http://{url}/login', status_code=status.HTTP_303_SEE_OTHER
        )
    if user['role'] == 'project_manager':
        return templates.TemplateResponse(
            'projects.html', 
            {
                'request': request, 
                'chief_editors_list': chief_editors_list, 
                'all_projects': projects, 
                'projects': projects_current_page, 
                'translators_list': translators_list, 
                'num_of_pages': num_of_pages, 
                'current_page': page,
                'archive': archive,
                'incorrect_time': incorrect_time,
                'incorrect_name': incorrect_name,
            }
        )
    return RedirectResponse(
        f'http://{url}', status_code=status.HTTP_303_SEE_OTHER
    )

@router.get("/project/{project_id}")
async def show_project(
    request: Request, 
    project_id: str, 
    incorrect_time: bool = False
):
    chief_editors_list = await users.get_list_of_users('chief_editor')
    translators_list = await users.get_list_of_users('translator')
    project =  await users.get_project_by_id(project_id)
    if project['status'] == 'finished':
        projects = await users.get_projects('finished')
    else:
        projects = await users.get_projects('created')
    projects = sorted(projects, key=lambda d: d['deadline']) 
    user = await users.get_current_user_from_cookie(request)
    project_activities = list(
        filter(
            lambda i: i['activity_name'] != 'initial_activity', 
            await users.get_activities_of_the_project(project['project_name'])
        )
    )
    project_translators = []
    for project_activity in project_activities:
        result = await users.get_user_by_id(project_activity['translator'])
        project_activity['translator'] = result['username']
        if result not in project_translators:
            project_translators.append(result)
    current_chief_editor = await users.get_user_by_id(project['editor'])
    if not user:
        return RedirectResponse(
            f'http://{url}/login', status_code=status.HTTP_303_SEE_OTHER
        )
    if user['role'] == 'project_manager':
        return templates.TemplateResponse(
            'project.html', 
            {
                'request': request, 
                'chief_editors_list': chief_editors_list, 
                'all_projects': projects, 
                'translators_list': translators_list, 
                'current_project_name': project['project_name'], 
                'current_chief_editor': current_chief_editor,
                'status': project['status'],
                'project_activities': project_activities,
                'project_id': project_id,
                'project_translators': project_translators,
                'incorrect_time': incorrect_time,
            }
        )
    return RedirectResponse(
        f'http://{url}', status_code=status.HTTP_303_SEE_OTHER
    )
    

@router.post("/create_project")
async def create_project(request: Request):
    result = await request.form()
    
    project_name = result['project_name']
    deadline = result['deadline'].split('-')
    if datetime.datetime.now() > datetime.datetime(
        int(deadline[0]), int(deadline[1]), int(deadline[2]), 0, 0
    ):
        return RedirectResponse(
            f'http://{url}/projects?incorrect_time=true', 
            status_code=status.HTTP_303_SEE_OTHER
        )
    project_names = await users.get_project_names()
    if project_name in project_names:
        return RedirectResponse(
            f'http://{url}/projects?incorrect_name=true', 
            status_code=status.HTTP_303_SEE_OTHER
        )
    editor = result['editor']
    activity = {
        'activity_name': 'initial_activity',
        'project_name': project_name,
        'translators': None,
        'editor': editor,
        'deadline': datetime.datetime(
            int(deadline[0]), int(deadline[1]), int(deadline[2]), 0, 0
        ),
        'project_status': 'created',
        'completeness': 0,
        'status': 'finished'
    }
    await users.create_activity(models.ActivityModel(**activity))
    return RedirectResponse(
        f'http://{url}/projects', status_code=status.HTTP_303_SEE_OTHER
    )

@router.post("/edit_project")
async def edit_project(request: Request):
    result = await request.form()
    project_name = result['project_name']
    deadline = result['deadline'].split('-')
    editor = result['editor']
    if datetime.datetime.now() > datetime.datetime(
        int(deadline[0]), int(deadline[1]), int(deadline[2]), 0, 0
    ):
        return RedirectResponse(
            f'http://{url}/projects?incorrect_time=true', 
            status_code=status.HTTP_303_SEE_OTHER
        )
    old_project = await users.get_project_by_id(result['_id'])
    project_names = await users.get_project_names()
    if (project_name in project_names and 
        project_name != old_project['project_name']):
        return RedirectResponse(
            f'http://{url}/projects?incorrect_name=true', 
            status_code=status.HTTP_303_SEE_OTHER
        )
    activity = {
        'activity_name': 'initial_activity',
        'project_name': project_name,
        'translators': None,
        'editor': editor,
        'deadline': datetime.datetime(
            int(deadline[0]), int(deadline[1]), int(deadline[2]), 0, 0
        ),
        'project_status': 'created',
        'completeness': 0,
        'status': 'finished'
    }
    await users.edit_project(
        models.ActivityModel(**activity), result['_id']
    )
    return RedirectResponse(
        f'http://{url}/projects', status_code=status.HTTP_303_SEE_OTHER
    )



@router.post("/sign-up", response_model=models.User)
async def app_create_user(user: models.UserCreate):
    db_user = await users.get_user_by_login(login=user.login)
    if db_user:
        raise HTTPException(status_code=400, detail="Login already registered")
    return await users.create_user(user=user)

@router.get('/login', response_class=HTMLResponse)
async def login(request: Request, not_valid: bool = False):
    user = await users.get_current_user_from_cookie(request)
    if user:
        return RedirectResponse(
            f'http://{url}/', status_code=status.HTTP_303_SEE_OTHER
        )
    return templates.TemplateResponse(
        'registration_page.html', {'request': request, 'not_valid': not_valid}
    )

@router.get('/forgot_password', response_class=HTMLResponse)
async def forgot_password(request: Request, not_valid: bool = False):
    return templates.TemplateResponse(
        'forgot_password.html', {'request': request, 'not_valid': not_valid}
    )

@router.post("/login_form")
async def auth(
        response: Response, 
        form_data: OAuth2PasswordRequestForm = Depends()
    ):
    user = await users.get_user_by_login(login=form_data.username)
    if not user:
        raise HTTPException(
            status_code=302, 
            detail="Incorrect login or password", 
            headers = {"Location": f"http://{url}/login?not_valid=true"}
        )
        
    if not users.validate_password(
        password=form_data.password, hashed_password=user["password"]
    ):
        raise HTTPException(
            status_code=302, 
            detail="Incorrect login or password", 
            headers = {"Location": f"http://{url}/login?not_valid=true"}
        )

    token = await users.create_user_token(
        user_id=users.user_helper(user)["id"]
    )
    response = RedirectResponse(
        f'http://{url}/', 
        status_code=status.HTTP_303_SEE_OTHER
    )
    response.set_cookie(
        key='Authorization',
        value=token,
        httponly=True,
        expires=86400
    )
    return response

@router.get("/me")
async def read_users_me(request: Request):
    user = await users.get_current_user_from_cookie(request)
    if user['role'] == 'translator':
        user_id = str(user['_id'])
        activities = await users.get_user_activities(user_id, 'translators')
        current_user = await users.get_user_by_id(user_id)
        return templates.TemplateResponse(
            'translator.html',
            {
                'request': request, 
                'activities': activities,
                'current_user': current_user
            }
        )
    if user['role'] == 'chief_editor':
        user_id = str(user['_id'])
        activities = await users.get_user_activities(user_id, 'editor')
        current_chief_editor = await users.get_user_by_id(user_id)
        return templates.TemplateResponse(
            'chief_editor.html', {
                'request': request,
                'current_chief_editor': current_chief_editor,
                'chief_editor_activities': activities,
            }
        )
    return RedirectResponse(
        f'http://{url}', status_code=status.HTTP_303_SEE_OTHER
    )

@router.post("/project/create_activity")
async def create_activity(request: Request):
    form = await request.form()
    deadline = form['deadline'].split('-')
    activity = {
        'activity_name': form['activity_name'],
        'project_name': form['project_name'],
        'translators': form['translator'],
        'editor': form['current_chief_editor'],
        'deadline': datetime.datetime(
            int(deadline[0]), int(deadline[1]), int(deadline[2]), 0, 0
        ),
        'project_status': 'in work',
        'completeness': 0.0,
        'status': 'created'
    }
    await users.create_activity(models.ActivityModel(**activity))
    return RedirectResponse(
        f"http://{url}/project/{form['project_id']}", 
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.post("/project/edit_activity")
async def edit_activity(request: Request):
    form = await request.form()
    deadline = form['deadline'].split('-')
    if datetime.datetime.now() > datetime.datetime(
        int(deadline[0]), int(deadline[1]), int(deadline[2]), 0, 0
    ):
        return RedirectResponse(
            f"http://{url}/project/{form['project_id']}?incorrect_time=true", 
            status_code=status.HTTP_303_SEE_OTHER
        )
    activity = {
        'activity_name': form['activity_name'],
        'project_name': form['project_name'],
        'translators': form['translator'],
        'editor': form['current_chief_editor'],
        'deadline': datetime.datetime(
            int(deadline[0]), int(deadline[1]), int(deadline[2]), 0, 0
        ),
        'project_status': 'in work',
        'completeness': 0.0,
        'status': 'created',
    }
    await users.edit_activity(
        models.ActivityModel(**activity), 
        form['activity_id']
    )
    return RedirectResponse(
        f"http://{url}/project/{form['project_id']}", 
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.post("/logout")
async def logout(response: Response):
    response_logout = RedirectResponse(
        f'http://{url}/login', 
        status_code=status.HTTP_303_SEE_OTHER
    )
    response_logout.delete_cookie(key='Authorization')
    return response_logout

@router.post("/project/logout")
async def project_logout(response: Response):
    response_logout = RedirectResponse(
        f'http://{url}/login', 
        status_code=status.HTTP_303_SEE_OTHER
    )
    response_logout.delete_cookie(key='Authorization')
    return response_logout

@router.post("/chief_editor/logout")
async def chief_editor_logout(response: Response):
    response_logout = RedirectResponse(
        f'http://{url}/login', 
        status_code=status.HTTP_303_SEE_OTHER
    )
    response_logout.delete_cookie(key='Authorization')
    return response_logout

@router.post("/translator/logout")
async def translator_logout(response: Response):
    response_logout = RedirectResponse(
        f'http://{url}/login', 
        status_code=status.HTTP_303_SEE_OTHER
    )
    response_logout.delete_cookie(key='Authorization')
    return response_logout

@router.get("/translator/{translator_id}")
async def show_translator(request: Request, translator_id: str):
    current_translator = await users.get_user_by_id(translator_id)
    chief_editors_list = await users.get_list_of_users('chief_editor')
    translators_list = await users.get_list_of_users('translator')
    projects = await users.get_projects('created')
    projects = sorted(projects, key=lambda d: d['deadline'])
    activities = await users.get_user_activities(translator_id, 'translators')
    user = await users.get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse(
            f'http://{url}/login', status_code=status.HTTP_303_SEE_OTHER
        )
    if user['role'] == 'project_manager':
        return templates.TemplateResponse(
            'translator_pm.html', 
            {
                'request': request,
                'chief_editors_list': chief_editors_list, 
                'all_projects': projects, 
                'translators_list': translators_list,
                'current_translator': current_translator['username'],
                'activities': activities,
            }
        )
    return RedirectResponse(
        f'http://{url}', status_code=status.HTTP_303_SEE_OTHER
    )

@router.get("/chief_editor/{chief_editor_id}")
async def show_chief_editor(request: Request, chief_editor_id: str):
    current_chief_editor = await users.get_user_by_id(chief_editor_id)
    chief_editors_list = await users.get_list_of_users('chief_editor')
    translators_list = await users.get_list_of_users('translator')
    projects = await users.get_projects('created')
    projects = sorted(projects, key=lambda d: d['deadline'])
    activities = await users.get_user_activities(chief_editor_id, 'editor')
    user = await users.get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse(
            f'http://{url}/login', status_code=status.HTTP_303_SEE_OTHER
        )
    if user['role'] == 'project_manager':
        return templates.TemplateResponse(
            'chief_editor_pm.html', 
            {
                'request': request,
                'chief_editors_list': chief_editors_list, 
                'all_projects': projects, 
                'translators_list': translators_list,
                'current_chief_editor': current_chief_editor,
                'chief_editor_activities': activities,
            }
        )
    return RedirectResponse(
        f'http://{url}', status_code=status.HTTP_303_SEE_OTHER
    )

@router.post("/project/change_chief_editor")
async def change_chief_editor(request: Request):
    result = await request.form()
    project = await users.get_project_by_id(result['_id'])
    activity = {
        'activity_name': 'initial_activity',
        'project_name': project['project_name'],
        'translators': None,
        'editor': result['editor'],
        'deadline': project['deadline'],
        'project_status': project['status'],
        'completeness': 0,
        'status': 'finished'
    }
    await users.edit_project(
        models.ActivityModel(**activity), result['_id']
    )
    return RedirectResponse(
        f"http://{url}/project/{result['_id']}",
        status_code=status.HTTP_303_SEE_OTHER
    )