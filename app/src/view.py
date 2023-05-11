from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates/")

def main_page(request: Request):
    return templates.TemplateResponse('test.html', {'request': request})

def projects_page(
    request: Request, chief_editors_list: list, projects: list, 
    projects_current_page: list, translators_list: list, num_of_pages: int, 
    page: int, archive: bool, incorrect_time: bool, incorrect_name: bool,
):
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

def project_page(
    request: Request, chief_editors_list: list, projects: list, 
    translators_list: list, project_name: str, current_chief_editor: str,
    status: str, project_activities: list, project_id: str, 
    project_translators: list, incorrect_time: bool,
):
    return templates.TemplateResponse(
        'project.html', 
        {
            'request': request, 
            'chief_editors_list': chief_editors_list, 
            'all_projects': projects, 
            'translators_list': translators_list, 
            'current_project_name': project_name, 
            'current_chief_editor': current_chief_editor,
            'status': status,
            'project_activities': project_activities,
            'project_id': project_id,
            'project_translators': project_translators,
            'incorrect_time': incorrect_time,
        }
    )

def registration_page(request: Request, not_valid: bool):
    return templates.TemplateResponse(
        'registration_page.html', {'request': request, 'not_valid': not_valid}
    )

def translator_page(request: Request, activities: list, current_user: str):
    return templates.TemplateResponse(
        'translator.html',
        {
            'request': request, 
            'activities': activities,
            'current_user': current_user
        }
    )

def chief_editor_page(
    request: Request, current_chief_editor: str, activities: list
):
    return templates.TemplateResponse(
        'chief_editor.html', {
            'request': request,
            'current_chief_editor': current_chief_editor,
            'chief_editor_activities': activities,
        }
    )

def translator_pm_page(
    request: Request, chief_editors_list: list, projects: list, 
    translators_list: list, username: str, activities: list
):
    return templates.TemplateResponse(
        'translator_pm.html', 
        {
            'request': request,
            'chief_editors_list': chief_editors_list, 
            'all_projects': projects, 
            'translators_list': translators_list,
            'current_translator': username,
            'activities': activities,
        }
    )

def chief_editor_pm_page(
    request: Request, chief_editors_list: list, projects: list, 
    translators_list: list, current_chief_editor: str, activities: list
):
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