import logging
import os

from comanage_api import ComanageApi

from swagger_server.__main__ import create_app, db
from swagger_server.db_models import ApiVersion, FabricCous, FabricPeople, FabricProjects, FabricRoles, \
    FabricProjectOwners, FabricProjectMembers

logger = logging.getLogger("Load DB")

api = ComanageApi(
    co_api_url=os.getenv('COMANAGE_API_URL'),
    co_api_user=os.getenv('COMANAGE_API_USER'),
    co_api_pass=os.getenv('COMANAGE_API_PASS'),
    co_api_org_id=os.getenv('COMANAGE_API_CO_ID'),
    co_api_org_name=os.getenv('COMANAGE_API_CO_NAME'),
    co_ssh_key_authenticator_id=os.getenv('COMANAGE_API_SSH_KEY_AUTHENTICATOR_ID')
)


def load_version():
    logger.info("Load/Update database table 'version' as ApiVersion")
    version = os.getenv('API_VERSION')
    gitsha1 = os.getenv('API_GITSHA1')
    api_version = ApiVersion.query.first()
    api_version.version = version
    api_version.gitsha1 = gitsha1
    db.session.commit()


def load_comanage_cous():
    logger.info("Load/Update database table 'comanage_cous' as FabricCous")
    co_cous = api.cous_view_per_co().get('Cous', [])
    for co_cou in co_cous:
        co_cou_id = co_cou.get('Id')
        fab_cou = FabricCous.query.filter_by(cou_id=co_cou_id).one_or_none()
        if fab_cou:
            logger.info("Update entry in 'comanage_cous' table for CouId: {0}".format(co_cou_id))
            found_cou = True
        else:
            logger.info("Create entry in 'comanage_cous' table for CouId: {0}".format(co_cou_id))
            found_cou = False
            fab_cou = FabricCous()
            fab_cou.cou_id = co_cou_id
            fab_cou.created_date = co_cou.get('Created')
        fab_cou.co_id = co_cou.get('CoId')
        fab_cou.name = co_cou.get('Name')
        fab_cou.description = co_cou.get('Description')
        fab_cou.version = co_cou.get('Version')
        fab_cou.parent_id = co_cou.get('ParentId', '-1')
        fab_cou.revision = co_cou.get('Revision')
        fab_cou.lft = co_cou.get('Lft')
        fab_cou.rght = co_cou.get('Rght')
        fab_cou.modified_date = co_cou.get('Modified')
        fab_cou.deleted = co_cou.get('Deleted')
        fab_cou.actor_identifier = co_cou.get('ActorIdentifier')
        if not found_cou:
            db.session.add(fab_cou)
        db.session.commit()
    db.session.commit()


def primary_name_from_coperson_id(co_person_id: int) -> str:
    primary_name = ''
    co_names = api.names_view_per_person(person_type='copersonid', person_id=co_person_id).get('Names', [])
    for co_name in co_names:
        if co_name.get('PrimaryName', False):
            family = co_name.get('Family', '')
            middle = co_name.get('Middle', '')
            given = co_name.get('Given', '')
            if middle:
                primary_name = given + ' ' + middle + ' ' + family
            else:
                primary_name = given + ' ' + family

    return primary_name


def official_email_from_coperson_id(co_person_id: int) -> str:
    official_email = ''
    co_emails = api.email_addresses_view_per_person(
        person_type='copersonid',
        person_id=co_person_id
    ).get('EmailAddresses', [])
    for co_email in co_emails:
        if co_email.get('Type') == 'official':
            official_email = co_email.get('Mail')
            break

    return official_email


def oidc_claim_sub_from_coperson_id(co_person_id: int) -> str:
    oidc_claim_sub = ''
    co_identifiers = api.identifiers_view_per_entity(
        entity_type='copersonid',
        entity_id=co_person_id
    ).get('Identifiers', [])
    for ident in co_identifiers:
        if ident.get('Type', None) == 'oidcsub':
            oidc_claim_sub = ident.get('Identifier', '')
            break

    return oidc_claim_sub


def load_fabric_people():
    logger.info("Load/Update database table 'fabric_people' as FabricPeople")
    co_people = api.copeople_view_per_co().get('CoPeople', [])
    for co_person in co_people:
        co_person_id = co_person.get('Id')
        fab_person = FabricPeople.query.filter_by(co_person_id=co_person_id).one_or_none()
        if fab_person:
            logger.info("Update entry in 'fabric_people' table for CouId: {0}".format(co_person_id))
            found_person = True
        else:
            logger.info("Create entry in 'fabric_people' table for CouId: {0}".format(co_person_id))
            found_person = False
            fab_person = FabricPeople()
            fab_person.co_id = co_person.get('CoId')
            fab_person.co_person_id = co_person_id
            fab_person.oidc_claim_sub = oidc_claim_sub_from_coperson_id(co_person_id)
        fab_person.email = official_email_from_coperson_id(co_person_id)
        fab_person.name = primary_name_from_coperson_id(co_person_id)
        fab_person.co_status = co_person.get('Status')
        if not found_person:
            logger.info("--> name: {0} | email: {1} | oidc_claim_sub {2}".format(
                fab_person.name, fab_person.email, fab_person.oidc_claim_sub))
            db.session.add(fab_person)
        db.session.commit()
    db.session.commit()


def load_fabric_roles():
    logger.info("Load/Update database table 'fabric_roles' as FabricRoles")
    query = FabricPeople.query.filter(FabricPeople.co_person_id != 0).all()
    co_person_ids = [q.co_person_id for q in query]
    for co_person_id in co_person_ids:
        person = FabricPeople.query.filter_by(co_person_id=co_person_id).one_or_none()
        co_roles = api.coperson_roles_view_per_coperson(coperson_id=co_person_id)
        if co_roles:
            co_roles = co_roles.get('CoPersonRoles', [])
            for co_role in co_roles:
                co_role_id = co_role.get('Id')
                co_cou_id = co_role.get('CouId')
                status = co_role.get('Status')
                if person and co_cou_id and status:
                    role = FabricRoles.query.filter_by(role_id=co_role_id).one_or_none()
                    if not role:
                        logger.info("Create entry in 'roles' table for CoPersonRolesId: {0}".format(co_role_id))
                        role = FabricRoles()
                        role_cou = FabricCous.query.filter_by(cou_id=co_cou_id).one_or_none()
                        if role_cou:
                            role.cou_id = role_cou.__asdict__().get('id')
                            role.role_name = role_cou.__asdict__().get('name')
                        else:
                            logger.warning("CoPersonRolesId: {0} is missing 'CouId'".format(co_role_id))
                            continue
                        role.role_id = co_role_id
                        role.people_id = person.id
                        role.status = status
                        db.session.add(role)
                        db.session.commit()
                    else:
                        logger.info("Update entry in 'roles' table for CoPersonRolesId: {0}".format(co_role_id))
                        role.status = status
                        db.session.commit()
                else:
                    logger.warning("CoPersonRolesId: {0} is missing 'CouId'".format(co_role_id))
    db.session.commit()


def load_fabric_projects():
    logger.info("Load/Update database table 'fabric_projects' as FabricProjects")
    proj_cous = FabricCous.query.filter(
        FabricCous.name.ilike('%' + '-pc'),
        FabricCous.parent_id == os.getenv('COU_ID_PROJECTS')
    ).order_by(FabricCous.name).all()
    if proj_cous:
        for proj_cou in proj_cous:
            d_proj_cou = proj_cou.__asdict__()
            proj_uuid, pc = d_proj_cou.get('name').rsplit('-', 1)
            if proj_uuid:
                # create/update fabric_project
                fab_project = FabricProjects.query.filter_by(uuid=proj_uuid).one_or_none()
                if fab_project:
                    logger.info("Update entry in 'fabric_project' table for UUID: {0}".format(proj_uuid))
                    found_project = True
                    fab_project.name = d_proj_cou.get('description')
                else:
                    logger.info("Create entry in 'fabric_project' table for UUID: {0}".format(proj_uuid))
                    found_project = False
                    fab_project = FabricProjects()
                    fab_project.uuid = proj_uuid
                    fab_project.name = d_proj_cou.get('description')
                    fab_project.description = d_proj_cou.get('description')
                    fab_project.facility = os.getenv('FABRIC_FACILITY')
                    fab_project.created_time = d_proj_cou.get('created_date')
                cb_id = FabricRoles.query.filter_by(
                    cou_id=d_proj_cou.get('id')
                ).first().__asdict__().get('people_id')
                fab_project.created_by = FabricPeople.query.filter_by(
                    id=cb_id
                ).one_or_none().__asdict__().get('uuid')
                if not found_project:
                    db.session.add(fab_project)
                db.session.commit()
                # create/update project_owners
                owner_roles = FabricRoles.query.filter_by(role_name=proj_uuid + '-po').all()
                if owner_roles:
                    for role in owner_roles:
                        role = role.__asdict__()
                        owner = FabricProjectOwners.query.filter(
                            FabricProjectOwners.projects_id == fab_project.id,
                            FabricProjectOwners.people_id == role.get('people_id')
                        ).one_or_none()
                        if not owner:
                            logger.info("Create entry in 'project_owners' table for UUID: {0}".format(proj_uuid))
                            owner = FabricProjectOwners()
                            owner.projects_id = fab_project.id
                            owner.people_id = role.get('people_id')
                            db.session.add(owner)
                            db.session.commit()
                # create/update project_members
                member_roles = FabricRoles.query.filter_by(role_name=proj_uuid + '-pm').all()
                if member_roles:
                    for role in member_roles:
                        role = role.__asdict__()
                        member = FabricProjectMembers.query.filter(
                            FabricProjectMembers.projects_id == fab_project.id,
                            FabricProjectMembers.people_id == role.get('people_id')
                        ).one_or_none()
                        if not member:
                            logger.info("Create entry in 'project_members' table for UUID: {0}".format(proj_uuid))
                            member = FabricProjectMembers()
                            member.projects_id = fab_project.id
                            member.people_id = role.get('people_id')
                            db.session.add(member)
                            db.session.commit()

    db.session.commit()


if __name__ == '__main__':
    logger.info("Start idempotent database load/update")
    app = create_app()
    app.app_context().push()
    load_version()
    load_comanage_cous()
    load_fabric_people()
    load_fabric_roles()
    load_fabric_projects()
    db.session.close()
