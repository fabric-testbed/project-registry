from configparser import ConfigParser

config = ConfigParser()
config.read('swagger_server/config/config.ini')


def comanage_projects_add_members_put(project_uuid, project_members):
    project_cou = 'CO:COU:' + str(project_uuid) + '-pm:members:active'
    return True


def comanage_projects_add_owners_put(project_uuid, project_owners):
    project_cou = 'CO:COU:' + str(project_uuid) + '-po:members:active'
    return True


def comanage_projects_remove_members_put(project_uuid, project_members):
    project_cou = 'CO:COU:' + str(project_uuid) + '-pm:members:active'
    return True


def comanage_projects_remove_owners_put(project_uuid, project_owners):
    project_cou = 'CO:COU:' + str(project_uuid) + '-po:members:active'
    return True


def comanage_create_cous():
    # check for valid cou pattern
    # attempt to create cous
    # return status
    pass


def comanage_remove_cous():
    # check for valid cou pattern
    # validate that cous are empty of users
    # attempt to remove cous
    # return status
    pass


def comanange_add_users_to_cou():
    # validate that cou exists
    # validate that users exist
    # attempt to add users to cou
    # return status
    pass


def comanage_remove_users_from_cou():
    # validate that cou exists
    # validate that users exist
    # attempt to remove users from cou
    # return status
    pass
