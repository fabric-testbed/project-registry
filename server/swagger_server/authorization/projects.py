from . import FACILITY_OPERATORS, PROJECT_LEADS
from .auth_utils import get_api_person


def authorize_projects_add_members_put(headers, uuid, created_by):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    # set project owners COU value
    project_owners_cou = 'CO:COU:' + str(uuid) + '-po:members:active'

    # project creator - allowed to add members to projects they created
    if created_by == api_person.uuid:
        print('[INFO] created_by')
        return True
    # project owners - allowed to add members to projects they are owners of
    if project_owners_cou in api_person.roles:
        print('[INFO] ' + project_owners_cou)
        return True
    # facility operators - allowed to perform all actions within project-registry
    if FACILITY_OPERATORS in api_person.roles:
        print('[INFO] ' + FACILITY_OPERATORS)
        return True

    # all others - not allowed to add project members
    return False


def filter_projects_add_members_put(headers, response):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return response


def authorize_projects_add_owners_put(headers, created_by):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))

    # project creator - allowed to add owners to projects they created
    if created_by == api_person.uuid:
        print('[INFO] created_by')
        return True
    # facility operators - allowed to perform all actions within project-registry
    if FACILITY_OPERATORS in api_person.roles:
        print('[INFO] ' + FACILITY_OPERATORS)
        return True

    # all others - not allowed to add project owners
    return False


def filter_projects_add_owners_put(headers, response):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return response


def authorize_projects_add_tags_put(headers, uuid, created_by):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    # set project owners COU value
    project_owners_cou = 'CO:COU:' + str(uuid) + '-po:members:active'
    # set project members COU value
    project_members_cou = 'CO:COU:' + str(uuid) + '-pm:members:active'

    # project creator - allowed to add tags to projects they created
    if created_by == api_person.uuid:
        print('[INFO] created_by')
        return True
    # project members - allowed to add tags to projects they are members of
    if project_members_cou in api_person.roles:
        print('[INFO] ' + project_members_cou)
        return True
    # project owners - allowed to add tags to projects they are owners of
    if project_owners_cou in api_person.roles:
        print('[INFO] ' + project_owners_cou)
        return True
    # facility operators - allowed to perform all actions within project-registry
    if FACILITY_OPERATORS in api_person.roles:
        print('[INFO] ' + FACILITY_OPERATORS)
        return True

    # all others - not allowed to add project members
    return False


def filter_projects_add_tags_put(headers, response):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return response


def authorize_projects_create_post(headers):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))

    # project leads - allowed to create projects
    if PROJECT_LEADS in api_person.roles:
        print('[INFO] ' + PROJECT_LEADS)
        return True
    # facility operators - allowed to perform all actions within project-registry
    if FACILITY_OPERATORS in api_person.roles:
        print('[INFO] ' + FACILITY_OPERATORS)
        return True

    # all others - not allowed to create projects
    return False


def filter_projects_create_post(headers, response):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return response


def authorize_projects_delete_delete(headers, created_by):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))

    # project creator - allowed to delete projects they created
    if created_by == api_person.uuid:
        print('[INFO] created_by')
        return True
    # facility operators - allowed to perform all actions within project-registry
    if FACILITY_OPERATORS in api_person.roles:
        print('[INFO] ' + FACILITY_OPERATORS)
        return True

    # all others - not allowed to add project owners
    return False


def filter_projects_delete_delete(headers, response):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return response


def authorize_projects_get(headers):
    # TODO: check if any authorization is required here at all
    # get api_user
    # api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return True


def filter_projects_get(headers, response):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return response


def authorize_projects_remove_members_put(headers, uuid, created_by):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    # set project owners COU value
    project_owners_cou = 'CO:COU:' + str(uuid) + '-po:members:active'

    # project creator - allowed to remove members to projects they created
    if created_by == api_person.uuid:
        print('[INFO] created_by')
        return True
    # project owners - allowed to remove members to projects they are owners of
    if project_owners_cou in api_person.roles:
        print('[INFO] ' + project_owners_cou)
        return True
    # facility operators - allowed to perform all actions within project-registry
    if FACILITY_OPERATORS in api_person.roles:
        print('[INFO] ' + FACILITY_OPERATORS)
        return True

    # all others - not allowed to add project members
    return False


def filter_projects_remove_members_put(headers, response):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return response


def authorize_projects_remove_owners_put(headers, created_by):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))

    # project creator - allowed to remove owners to projects they created
    if created_by == api_person.uuid:
        print('[INFO] created_by')
        return True
    # facility operators - allowed to perform all actions within project-registry
    if FACILITY_OPERATORS in api_person.roles:
        print('[INFO] ' + FACILITY_OPERATORS)
        return True

    # all others - not allowed to add project owners
    return False


def filter_projects_remove_owners_put(headers, response):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return response


def authorize_projects_remove_tags_put(headers, uuid, created_by):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    # set project owners COU value
    project_owners_cou = 'CO:COU:' + str(uuid) + '-po:members:active'
    # set project members COU value
    project_members_cou = 'CO:COU:' + str(uuid) + '-pm:members:active'

    # project creator - allowed to remove tags to projects they created
    if created_by == api_person.uuid:
        print('[INFO] created_by')
        return True
    # project members - allowed to remove tags to projects they are members of
    if project_members_cou in api_person.roles:
        print('[INFO] ' + project_members_cou)
        return True
    # project owners - allowed to remove tags to projects they are owners of
    if project_owners_cou in api_person.roles:
        print('[INFO] ' + project_owners_cou)
        return True
    # facility operators - allowed to perform all actions within project-registry
    if FACILITY_OPERATORS in api_person.roles:
        print('[INFO] ' + FACILITY_OPERATORS)
        return True

    # all others - not allowed to add project members
    return False


def filter_projects_remove_tags_put(headers, response):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return response


def authorize_projects_update_put(headers, created_by):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))

    # project creator - allowed to update projects they created
    if created_by == api_person.uuid:
        print('[INFO] created_by')
        return True
    # facility operators - allowed to perform all actions within project-registry
    if FACILITY_OPERATORS in api_person.roles:
        print('[INFO] ' + FACILITY_OPERATORS)
        return True

    # all others - not allowed to add project owners
    return False


def filter_projects_update_put(headers, response):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return response


def authorize_projects_uuid_get(headers, uuid, created_by):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    # set project owners COU value
    project_owners_cou = 'CO:COU:' + str(uuid) + '-po:members:active'
    # set project members COU value
    project_members_cou = 'CO:COU:' + str(uuid) + '-pm:members:active'

    # project creator - allowed to get details about projects they created
    if created_by == api_person.uuid:
        print('[INFO] created_by')
        return True
    # project members - allowed to get details about projects they are members of
    if project_members_cou in api_person.roles:
        print('[INFO] ' + project_members_cou)
        return True
    # project owners - allowed to get details about projects they are owners of
    if project_owners_cou in api_person.roles:
        print('[INFO] ' + project_owners_cou)
        return True
    # facility operators - allowed to perform all actions within project-registry
    if FACILITY_OPERATORS in api_person.roles:
        print('[INFO] ' + FACILITY_OPERATORS)
        return True

    # all others - not allowed to add project members
    return False


def filter_projects_uuid_get(headers, response):
    # get api_user
    api_person = get_api_person(headers.get('X-Vouch-Idp-Idtoken'))
    return response
