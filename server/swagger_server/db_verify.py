import logging
import os

from comanage_api import ComanageApi

from swagger_server.__main__ import create_app, db
from swagger_server.db_models import FabricProjects, FabricRoles, FabricProjectOwners, FabricProjectMembers, \
    FabricCous, FabricPeople

logger = logging.getLogger("Verify DB")

api = ComanageApi(
    co_api_url=os.getenv('COMANAGE_API_URL'),
    co_api_user=os.getenv('COMANAGE_API_USER'),
    co_api_pass=os.getenv('COMANAGE_API_PASS'),
    co_api_org_id=os.getenv('COMANAGE_API_CO_ID'),
    co_api_org_name=os.getenv('COMANAGE_API_CO_NAME'),
    co_ssh_key_authenticator_id=os.getenv('COMANAGE_API_SSH_KEY_AUTHENTICATOR_ID')
)


def verify_fabric_roles():
    logger.info("Verify database table 'fabric_roles' as FabricRoles")
    fab_roles = FabricRoles.query.all()
    for fab_role in fab_roles:
        if fab_role.role_id > 0:
            try:
                co_person_role = api.coperson_roles_view_one(coperson_role_id=fab_role.role_id)
            except Exception as e:
                logger.error(e)
                co_person_role = None
        else:
            logger.info("Invalid entry in 'roles' table for CoPersonRolesId: {0}".format(fab_role.role_id))
            continue
        if co_person_role:
            logger.info("Verify entry in 'roles' table for CoPersonRolesId: {0}".format(fab_role.role_id))
            co_person_role = co_person_role.get('CoPersonRoles')[0]
            if co_person_role.get('Deleted'):
                people_id = fab_role.people_id
                # check for -po or -pm and remove from projects_{owners, members} table
                if fab_role.role_name[-3:] == '-po':
                    project_id = FabricProjects.query.filter_by(uuid=fab_role.role_name[:-3]).first().id
                    po = FabricProjectOwners.query.filter(
                        FabricProjectOwners.people_id == people_id,
                        FabricProjectOwners.projects_id == project_id
                    ).one_or_none()
                    if po:
                        logger.warning(
                            "Delete entry in 'project_owners' table for CoPersonRolesId: {0}".format(fab_role.role_id))
                        db.session.delete(po)
                elif fab_role.role_name[-3:] == '-pm':
                    project_id = FabricProjects.query.filter_by(uuid=fab_role.role_name[:-3]).first().id
                    pm = FabricProjectMembers.query.filter(
                        FabricProjectMembers.people_id == people_id,
                        FabricProjectMembers.projects_id == project_id
                    ).one_or_none()
                    if pm:
                        logger.warning(
                            "Delete entry in 'project_members' table for CoPersonRolesId: {0}".format(fab_role.role_id))
                        db.session.delete(pm)
                # remove from fabric_roles table
                logger.warning("Delete entry in 'fabric_roles' table for CoPersonRolesId: {0}".format(fab_role.role_id))
                db.session.delete(fab_role)
                db.session.commit()
        else:
            logger.error("Invalid entry in 'roles' table for CoPersonRolesId: {0}".format(fab_role.role_id))


def verify_fabric_cous():
    logger.info("Verify database table 'comanage_cous' as FabricCous")
    fab_cous = FabricCous.query.all()
    for fab_cou in fab_cous:
        try:
            co_cou = api.cous_view_one(cou_id=fab_cou.cou_id)
        except Exception as e:
            logger.error(e)
            co_cou = None
        if co_cou:
            logger.info("Verify entry in 'comanage_cous' table for CouId: {0}".format(fab_cou.cou_id))
            co_cou = co_cou.get('Cous')[0]
            if co_cou.get('Deleted'):
                # remove entry if COU marked as deleted
                logger.warning("Delete entry in 'comanage_cous' table for CouId: {0}".format(fab_cou.cou_id))
                db.session.delete(fab_cou)
                db.session.commit()
        else:
            # remove entry if COU cannot be found in COmanage
            logger.info("Invalid entry in 'comanage_cous' table for CouId: {0}".format(fab_cou.cou_id))
            logger.warning("Delete entry in 'comanage_cous' table for CouId: {0}".format(fab_cou.cou_id))
            db.session.delete(fab_cou)
            db.session.commit()


def verify_fabric_people():
    logger.info("Verify database table 'fabric_people' as FabricPeople")
    fab_people = FabricPeople.query.all()
    for fab_person in fab_people:
        if fab_person.co_person_id > 0:
            try:
                co_person = api.copeople_view_one(coperson_id=fab_person.co_person_id)
            except Exception as e:
                logger.error(e)
                co_person = None
        else:
            logger.info("Invalid entry in 'fabric_people' table for CoPersonId: {0}".format(fab_person.co_person_id))
            continue
        if co_person:
            logger.info("Verify entry in 'fabric_people' table for CoPersonId: {0}".format(fab_person.co_person_id))
            co_person = co_person.get('CoPeople')[0]
            if co_person.get('Deleted'):
                logger.warning(
                    "Delete entry in 'fabric_people' table for CoPersonId: {0}".format(fab_person.co_person_id))
                db.session.delete(fab_person)
                db.session.commit()


if __name__ == '__main__':
    logger.info("Start idempotent database verify")
    app = create_app()
    app.app_context().push()
    verify_fabric_roles()
    verify_fabric_cous()
    verify_fabric_people()
    db.session.close()
