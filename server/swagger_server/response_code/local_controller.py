import os
from datetime import datetime, timezone
from uuid import uuid4

from comanage_api import ComanageApi

from swagger_server.db import db
from swagger_server.db_models import FabricPeople, FabricProjects, FabricRoles, FabricCous, FabricTags, \
    FabricProjectOwners, FabricProjectMembers
from swagger_server.models.people_short import PeopleShort
from swagger_server.models.project_long import ProjectLong
from swagger_server.models.project_short import ProjectShort

api = ComanageApi(
    co_api_url=os.getenv('COMANAGE_API_URL'),
    co_api_user=os.getenv('COMANAGE_API_USER'),
    co_api_pass=os.getenv('COMANAGE_API_PASS'),
    co_api_org_id=os.getenv('COMANAGE_API_CO_ID'),
    co_api_org_name=os.getenv('COMANAGE_API_CO_NAME'),
    co_ssh_key_authenticator_id=os.getenv('COMANAGE_API_SSH_KEY_AUTHENTICATOR_ID')
)


def get_person_by_uuid(person_uuid: str) -> PeopleShort:
    person = PeopleShort()
    fab_person = FabricPeople.query.filter_by(uuid=person_uuid).one_or_none()
    if fab_person:
        d_person = fab_person.__asdict__()
        person.email = d_person.get('email')
        person.name = d_person.get('name')
        person.uuid = d_person.get('uuid')

    return person


def get_project_owners(project_id: int) -> [PeopleShort]:
    project_owners = []
    fab_owners = FabricProjectOwners.query.filter_by(projects_id=project_id)
    if fab_owners:
        owner_ids = []
        for o in fab_owners:
            owner_ids.append(o.__asdict__().get('people_id'))
        fab_people = FabricPeople.query.filter(FabricPeople.id.in_(owner_ids)).order_by(FabricPeople.name)
        if fab_people:
            for fab_person in fab_people:
                project_owners.append(get_person_by_uuid(fab_person.__asdict__().get('uuid')))

    return project_owners


def get_project_members(project_id: int) -> [PeopleShort]:
    project_members = []
    fab_members = FabricProjectMembers.query.filter_by(projects_id=project_id)
    if fab_members:
        member_ids = []
        for o in fab_members:
            member_ids.append(o.__asdict__().get('people_id'))
        fab_people = FabricPeople.query.filter(FabricPeople.id.in_(member_ids)).order_by(FabricPeople.name)
        if fab_people:
            for fab_person in fab_people:
                project_members.append(get_person_by_uuid(fab_person.__asdict__().get('uuid')))

    return project_members


def add_members_by_project_uuid(project_uuid: str, project_members: [str]) -> None:
    fab_project = FabricProjects.query.filter_by(uuid=project_uuid).first()
    member_cou = FabricCous.query.filter_by(name=project_uuid + '-pm').first()
    if not project_members:
        project_members = []
    for member in project_members:
        person = FabricPeople.query.filter_by(uuid=member).one_or_none()
        if person:
            people_id = person.__asdict__().get('id')
            co_person_id = person.__asdict__().get('co_person_id')
        else:
            print("[ERROR] Person Not Found member for Project: {0}, member: {1}".format(project_uuid, member))
            continue
        fab_member = FabricProjectMembers.query.filter(
            FabricProjectMembers.projects_id == fab_project.id,
            FabricProjectMembers.people_id == people_id
        ).one_or_none()
        if fab_member:
            print("[WARNING] Duplicate member for Project: {0}, member: {1}".format(project_uuid, member))
        else:
            print("[INFO] Create member for Project: {0}, member: {1}".format(project_uuid, member))
            # create new role in COmanage
            co_response = api.coperson_roles_add(
                coperson_id=co_person_id, cou_id=member_cou.cou_id,
                status='Active', affiliation='member')
            if co_response:
                role_id = co_response.get('Id')
                # update fabric_roles table
                update_fabric_roles_by_role_id(people_id=people_id, role_id=role_id)
                # update project_members table
                pm = FabricProjectMembers()
                pm.projects_id = fab_project.id
                pm.people_id = people_id
                db.session.add(pm)
                db.session.commit()
            else:
                print("[ERROR] CoPersonRole Not Created for member: {0}".format(member))


def remove_members_by_project_uuid(project_uuid: str, project_members: [str]) -> None:
    fab_project = FabricProjects.query.filter_by(uuid=project_uuid).first()
    member_cou = FabricCous.query.filter_by(name=project_uuid + '-pm').first()
    if not project_members:
        project_members = []
    for member in project_members:
        person = FabricPeople.query.filter_by(uuid=member).one_or_none()
        if person:
            people_id = person.__asdict__().get('id')
        else:
            print("[WARNING] Member not found for Project: {0}, member: {1}".format(project_uuid, member))
            continue
        fab_member = FabricProjectMembers.query.filter(
            FabricProjectMembers.projects_id == fab_project.id,
            FabricProjectMembers.people_id == people_id
        ).one_or_none()
        if fab_member:
            print("[INFO] Remove member for Project: {0}, member: {1}".format(project_uuid, member))
            # remove role from COmanage
            fab_role = FabricRoles.query.filter(
                FabricRoles.role_name == member_cou.name,
                FabricRoles.people_id == people_id,
                FabricRoles.cou_id == member_cou.id
            ).one_or_none()
            if fab_role:
                role_id = fab_role.__asdict__().get('role_id')
                co_response = api.coperson_roles_delete(coperson_role_id=role_id)
                if co_response:
                    pass
                    # remove member from fabric_roles table
                    db.session.delete(fab_role)
                    # remove member from project_members table
                    db.session.delete(fab_member)
                    db.session.commit()
            else:
                print("[ERROR] CoPersonRole Not Found for member: {0}".format(member))
        else:
            print("[WARNING] Member not found for Project: {0}, member: {1}".format(project_uuid, member))


def add_owners_by_project_uuid(project_uuid: str, project_owners: [str]) -> None:
    fab_project = FabricProjects.query.filter_by(uuid=project_uuid).first()
    owner_cou = FabricCous.query.filter_by(name=project_uuid + '-po').first()
    if not project_owners:
        project_owners = []
    for owner in project_owners:
        person = FabricPeople.query.filter_by(uuid=owner).one_or_none()
        if person:
            people_id = person.__asdict__().get('id')
            co_person_id = person.__asdict__().get('co_person_id')
        else:
            print("[ERROR] Person Not Found owner for Project: {0}, owner: {1}".format(project_uuid, owner))
            continue
        fab_owner = FabricProjectOwners.query.filter(
            FabricProjectOwners.projects_id == fab_project.id,
            FabricProjectOwners.people_id == people_id
        ).one_or_none()
        if fab_owner:
            print("[WARNING] Duplicate owner for Project: {0}, owner: {1}".format(project_uuid, owner))
        else:
            print("[INFO] Create owner for Project: {0}, owner: {1}".format(project_uuid, owner))
            # create new role in COmanage
            co_response = api.coperson_roles_add(
                coperson_id=co_person_id, cou_id=owner_cou.cou_id,
                status='Active', affiliation='member')
            if co_response:
                role_id = co_response.get('Id')
                # update fabric_roles table
                update_fabric_roles_by_role_id(people_id=people_id, role_id=role_id)
                # update project_owners table
                po = FabricProjectOwners()
                po.projects_id = fab_project.id
                po.people_id = people_id
                db.session.add(po)
                db.session.commit()
            else:
                print("[ERROR] CoPersonRole Not Created for owner: {0}".format(owner))


def remove_owners_by_project_uuid(project_uuid: str, project_owners: [str]) -> None:
    fab_project = FabricProjects.query.filter_by(uuid=project_uuid).first()
    owner_cou = FabricCous.query.filter_by(name=project_uuid + '-po').first()
    if not project_owners:
        project_owners = []
    for owner in project_owners:
        person = FabricPeople.query.filter_by(uuid=owner).one_or_none()
        if person:
            people_id = person.__asdict__().get('id')
        else:
            print("[WARNING] Owner not found for Project: {0}, owner: {1}".format(project_uuid, owner))
            continue
        fab_owner = FabricProjectOwners.query.filter(
            FabricProjectOwners.projects_id == fab_project.id,
            FabricProjectOwners.people_id == people_id
        ).one_or_none()
        if fab_owner:
            print("[INFO] Remove Owner for Project: {0}, owner: {1}".format(project_uuid, owner))
            # remove role from COmanage
            fab_role = FabricRoles.query.filter(
                FabricRoles.role_name == owner_cou.name,
                FabricRoles.people_id == people_id,
                FabricRoles.cou_id == owner_cou.id
            ).one_or_none()
            if fab_role:
                role_id = fab_role.__asdict__().get('role_id')
                co_response = api.coperson_roles_delete(coperson_role_id=role_id)
                if co_response:
                    # remove member from fabric_roles table
                    db.session.delete(fab_role)
                    # remove member from project_owners table
                    db.session.delete(fab_owner)
                    db.session.commit()
            else:
                print("[ERROR] CoPersonRole Not Found for owner: {0}".format(owner))
        else:
            print("[WARNING] Owner not found for Project: {0}, owner: {1}".format(project_uuid, owner))


def add_creator_by_project_uuid(project_uuid: str, project_creator: str) -> None:
    creator_cou = FabricCous.query.filter_by(name=project_uuid + '-pc').first()
    if project_creator:
        person = FabricPeople.query.filter_by(uuid=project_creator).one_or_none()
        if person:
            people_id = person.__asdict__().get('id')
            co_person_id = person.__asdict__().get('co_person_id')
            fab_creator = FabricRoles.query.filter(
                FabricRoles.people_id == people_id,
                FabricRoles.cou_id == creator_cou.id,
                FabricRoles.role_name == project_uuid + '-pc'
            ).one_or_none()
            if fab_creator:
                print(
                    "[WARNING] Duplicate creator for Project: {0}, creator: {1}".format(project_uuid, project_creator))
            else:
                print("[INFO] Create creator for Project: {0}, creator: {1}".format(project_uuid, project_creator))
                # create new role in COmanage
                co_response = api.coperson_roles_add(
                    coperson_id=co_person_id, cou_id=creator_cou.cou_id,
                    status='Active', affiliation='member')
                if co_response:
                    role_id = co_response.get('Id')
                    # update fabric_roles table
                    update_fabric_roles_by_role_id(people_id=people_id, role_id=role_id)
                else:
                    print("[ERROR] CoPersonRole Not Created for creator: {0}".format(project_creator))
        else:
            print(
                "[ERROR] Person Not Found creator for Project: {0}, creator: {1}".format(project_uuid, project_creator))
    else:
        print("[ERROR] Person Not Found creator for Project: {0}, creator: {1}".format(project_uuid, project_creator))


def remove_creator_by_project_uuid(project_uuid: str, project_creator: str) -> None:
    creator_cou = FabricCous.query.filter_by(name=project_uuid + '-pc').first()
    if project_creator:
        person = FabricPeople.query.filter_by(uuid=project_creator).one_or_none()
        if person:
            people_id = person.__asdict__().get('id')
            fab_role = FabricRoles.query.filter(
                FabricRoles.people_id == people_id,
                FabricRoles.cou_id == creator_cou.id,
                FabricRoles.role_name == project_uuid + '-pc'
            ).one_or_none()
            if fab_role:
                # removed new role in COmanage
                role_id = fab_role.__asdict__().get('role_id')
                co_response = api.coperson_roles_delete(coperson_role_id=role_id)
                if co_response:
                    print("[INFO] CoPersonRole removed for creator: {0}".format(project_creator))
                    # remove creator from fabric_roles table
                    db.session.delete(fab_role)
                    db.session.commit()
                else:
                    print("[ERROR] CoPersonRole Not removed for creator: {0}".format(project_creator))
            else:
                print("[ERROR] Person Not Found creator for Project: {0}, creator: {1}".format(project_uuid,
                                                                                               project_creator))
        else:
            print(
                "[ERROR] Person Not Found creator for Project: {0}, creator: {1}".format(project_uuid, project_creator))
    else:
        print("[ERROR] Person Not Found creator for Project: {0}, creator: {1}".format(project_uuid, project_creator))


def project_create(name: str, description: str, facility: str, tags: [str], project_creator: str,
                   project_owners: [str], project_members: [str]) -> str:
    # generate uuid
    project_uuid = uuid4()
    # create -pc, -po, -pm COUs in COmanage and add to comanage_cous table
    cou_pc = api.cous_add(name=str(project_uuid) + '-pc', description=name, parent_id=os.getenv('COU_ID_PROJECTS'))
    if cou_pc:
        update_comanage_cous_by_cou_id(cou_pc.get('Id'))
    cou_po = api.cous_add(name=str(project_uuid) + '-po', description=name, parent_id=os.getenv('COU_ID_PROJECTS'))
    if cou_po:
        update_comanage_cous_by_cou_id(cou_po.get('Id'))
    cou_pm = api.cous_add(name=str(project_uuid) + '-pm', description=name, parent_id=os.getenv('COU_ID_PROJECTS'))
    if cou_pm:
        update_comanage_cous_by_cou_id(cou_pm.get('Id'))
    # create base project - uuid, name, description, facility, created_by, created_time
    if facility != os.getenv('FABRIC_FACILITY'):
        facility = os.getenv('FABRIC_FACILITY')
    project = FabricProjects()
    project.uuid = project_uuid
    project.name = name
    project.description = description
    project.facility = facility
    project.created_by = project_creator
    project.created_time = datetime.now(tz=timezone.utc)
    db.session.add(project)
    db.session.commit()
    # add project_creator to CoPersonRoles
    if not project_owners:
        project_owners = []
    if not project_members:
        project_members = []
    add_creator_by_project_uuid(project_uuid=str(project_uuid), project_creator=project_creator)
    # add project_owners
    if project_creator not in project_owners:
        project_owners.append(project_creator)
    if project_owners:
        add_owners_by_project_uuid(project_uuid=str(project_uuid), project_owners=project_owners)
    # add project_members
    if project_members:
        add_members_by_project_uuid(project_uuid=str(project_uuid), project_members=project_members)
    # add tags
    if tags:
        add_tags_by_project_uuid(project_uuid=str(project_uuid), tags=tags)
    # return project UUID

    return str(project_uuid)


def project_delete(project_uuid: str) -> bool:
    project = FabricProjects.query.filter_by(uuid=project_uuid).first()
    if project:
        print("[INFO] Delete Project: {0}".format(project_uuid))
        # remove tags from database
        query = FabricTags.query.filter_by(projects_id=project.id).all()
        tags = [q.tag for q in query]
        remove_tags_by_project_uuid(project_uuid=project_uuid, tags=tags)
        # for each project_member delete COmanage role and remove entry from fabric_roles and project_members
        query = FabricProjectMembers.query.filter_by(projects_id=project.id).all()
        pm_ids = [q.people_id for q in query]
        query = FabricPeople.query.filter(FabricPeople.id.in_(pm_ids)).all()
        project_members = [q.uuid for q in query]
        remove_members_by_project_uuid(project_uuid=project_uuid, project_members=project_members)
        # remove -pm COU
        pm_cou = FabricCous.query.filter_by(name=project_uuid + '-pm').one_or_none()
        if pm_cou:
            cou_id = pm_cou.__asdict__().get('cou_id')
            remove_pm_cou = api.cous_delete(cou_id=cou_id)
            if remove_pm_cou:
                print("[INFO] Remove -pm CO entry for CouId: {0}".format(cou_id))
                db.session.delete(pm_cou)
                db.session.commit()
            else:
                print("[WARNING] Not Found -pm CO entry for CouId: {0}".format(cou_id))
        # for each project_owner delete COmanage role and remove entry from fabric_roles and project_owners
        query = FabricProjectOwners.query.filter_by(projects_id=project.id).all()
        po_ids = [q.people_id for q in query]
        query = FabricPeople.query.filter(FabricPeople.id.in_(po_ids)).all()
        project_owners = [q.uuid for q in query]
        remove_owners_by_project_uuid(project_uuid=project_uuid, project_owners=project_owners)
        # remove -po COU
        po_cou = FabricCous.query.filter_by(name=project_uuid + '-po').one_or_none()
        if po_cou:
            cou_id = po_cou.__asdict__().get('cou_id')
            remove_pm_cou = api.cous_delete(cou_id=cou_id)
            if remove_pm_cou:
                print("[INFO] Remove -po CO entry for CouId: {0}".format(cou_id))
                db.session.delete(po_cou)
                db.session.commit()
            else:
                print("[WARNING] Not Found -po CO entry for CouId: {0}".format(cou_id))
        # for each project creator delete COmanage role and remove from fabric_roles
        remove_creator_by_project_uuid(project_uuid=project_uuid, project_creator=project.created_by)
        # remove -pc COU
        pc_cou = FabricCous.query.filter_by(name=project_uuid + '-pc').one_or_none()
        if pc_cou:
            cou_id = pc_cou.__asdict__().get('cou_id')
            remove_pm_cou = api.cous_delete(cou_id=cou_id)
            if remove_pm_cou:
                print("[INFO] Remove -pc CO entry for CouId: {0}".format(cou_id))
                db.session.delete(pc_cou)
                db.session.commit()
            else:
                print("[WARNING] Not Found -pc CO entry for CouId: {0}".format(cou_id))
        # remove project from fabric_projects
        db.session.delete(project)
        db.session.commit()
    else:
        print("[WARNING] UUID for Project: {0} Not Found".format(project_uuid))
        return False

    return True


def get_project_tags(project_id: int) -> [str]:
    tags = []
    project_tags = FabricTags.query.filter_by(projects_id=project_id).order_by(FabricTags.tag)
    if project_tags:
        for tag in project_tags:
            tags.append(tag.__asdict__().get('tag'))

    return tags


def add_tags_by_project_uuid(project_uuid: str, tags: [str]) -> bool:
    fab_project = FabricProjects.query.filter_by(uuid=project_uuid).first().__asdict__()
    project_id = fab_project.get('id')
    if not tags: tags = []
    for tag in tags:
        fab_tag = FabricTags.query.filter(
            FabricTags.projects_id == project_id,
            FabricTags.tag == tag
        ).one_or_none()
        if fab_tag:
            print("[WARNING] Duplicate tag for Project: {0}, tag: {1}".format(project_uuid, tag))
        else:
            print("[INFO] Create tag for Project: {0}, tag: {1}".format(project_uuid, tag))
            fab_tag = FabricTags()
            fab_tag.projects_id = project_id
            fab_tag.tag = tag
            db.session.add(fab_tag)
            db.session.commit()

    return True


def remove_tags_by_project_uuid(project_uuid: str, tags: [str]) -> bool:
    fab_project = FabricProjects.query.filter_by(uuid=project_uuid).first().__asdict__()
    project_id = fab_project.get('id')
    if not tags: tags = []
    for tag in tags:
        fab_tag = FabricTags.query.filter(
            FabricTags.projects_id == project_id,
            FabricTags.tag == tag
        ).one_or_none()
        if fab_tag:
            print("[INFO] Remove tag for Project: {0}, tag: {1}".format(project_uuid, tag))
            db.session.delete(fab_tag)
            db.session.commit()
        else:
            print("[WARNING] Not Found tag for Project: {0}, tag: {1}".format(project_uuid, tag))

    return True


def get_project_long_by_uuid(project_uuid: str) -> ProjectLong:
    pl = ProjectLong()
    project = FabricProjects.query.filter_by(uuid=project_uuid).first().__asdict__()
    project_id = project.get('id')
    pl.uuid = project_uuid
    pl.name = project.get('name')
    pl.description = project.get('description')
    pl.facility = project.get('facility')
    pl.created_time = project.get('created_time')
    pl.created_by = get_person_by_uuid(project.get('created_by'))
    pl.project_owners = get_project_owners(project_id)
    pl.project_members = get_project_members(project_id)
    pl.tags = get_project_tags(project_id)

    return pl


def get_project_short_by_uuid(project_uuid: str) -> ProjectShort:
    ps = ProjectShort()
    project = FabricProjects.query.filter_by(uuid=project_uuid).first().__asdict__()
    ps.uuid = project_uuid
    ps.name = project.get('name')
    ps.description = project.get('description')
    ps.facility = project.get('facility')
    ps.created_time = project.get('created_time')
    ps.created_by = get_person_by_uuid(project.get('created_by'))

    return ps


def update_comanage_cous_by_cou_id(cou_id: int) -> None:
    co_cous = api.cous_view_one(cou_id=cou_id).get('Cous', [])
    for co_cou in co_cous:
        co_cou_id = co_cou.get('Id')
        fab_cou = FabricCous.query.filter_by(cou_id=co_cou_id).one_or_none()
        if fab_cou:
            print("[INFO] Update entry in 'comanage_cous' table for CouId: {0}".format(co_cou_id))
            found_cou = True
        else:
            print("[INFO] Create entry in 'comanage_cous' table for CouId: {0}".format(co_cou_id))
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
        fab_cou.deleted = co_cou.get('Deleted')
        fab_cou.actor_identifier = co_cou.get('ActorIdentifier')
        fab_cou.lft = co_cou.get('Lft')
        fab_cou.rght = co_cou.get('Rght')
        fab_cou.modified_date = co_cou.get('Modified')
        if not found_cou:
            db.session.add(fab_cou)
        db.session.commit()


def update_fabric_roles_by_role_id(people_id: int, role_id: int) -> None:
    co_roles = api.coperson_roles_view_one(coperson_role_id=role_id)
    if co_roles:
        co_roles = co_roles.get('CoPersonRoles', [])
        for co_role in co_roles:
            co_role_id = co_role.get('Id')
            co_cou_id = co_role.get('CouId')
            status = co_role.get('Status')
            if people_id and co_cou_id and status:
                role = FabricRoles.query.filter_by(role_id=co_role_id).one_or_none()
                if not role:
                    print("[INFO] Create entry in 'roles' table for CoPersonRolesId: {0}".format(co_role_id))
                    role = FabricRoles()
                    role_cou = FabricCous.query.filter_by(cou_id=co_cou_id).one_or_none()
                    role.role_id = co_role_id
                    role.people_id = people_id
                    role.cou_id = role_cou.__asdict__().get('id')
                    role.role_name = role_cou.__asdict__().get('name')
                    role.status = status
                    db.session.add(role)
                    db.session.commit()
                else:
                    print("[INFO] Update entry in 'roles' table for CoPersonRolesId: {0}".format(co_role_id))
                    role.status = status
                    db.session.commit()
            else:
                print("[INFO] CoPersonRolesId: {0} is missing 'CouId'".format(co_role_id))


def update_project_by_project_uuid(project_uuid: str, name: str, description: str, facility: str) -> bool:
    fab_project = FabricProjects.query.filter_by(uuid=project_uuid).first()
    if name and name != fab_project.name:
        print("[INFO] Update name for Project: {0}, name: {1}".format(project_uuid, name))
        # update COmanage COUs
        fab_cous = FabricCous.query.filter(FabricCous.name.ilike(project_uuid + '%')).all()
        for cou in fab_cous:
            d_cou = cou.__asdict__()
            cou_id = d_cou.get('cou_id')
            is_updated = api.cous_edit(cou_id=cou_id, description=name)
            if is_updated:
                update_comanage_cous_by_cou_id(cou_id=cou_id)
        fab_project.name = name
    if description and description != fab_project.description:
        print("[INFO] Update description for Project: {0}, name: {1}".format(project_uuid, description))
        fab_project.description = description
    if facility and facility != fab_project.facility:
        print("[INFO] Update facility for Project: {0}, name: {1}".format(project_uuid, facility))
        if facility != os.getenv('FABRIC_FACILITY'):
            facility = os.getenv('FABRIC_FACILITY')
        fab_project.facility = facility

    db.session.commit()

    return True


def sync_roles_per_person(person_uuid: str) -> bool:
    person = FabricPeople.query.filter_by(uuid=person_uuid).one_or_none()
    if person:
        person = person.__asdict__()
        person_uuid = person.get('uuid')
        co_person_id = person.get('co_person_id')
        co_person_roles = api.coperson_roles_view_per_coperson(coperson_id=co_person_id).get('CoPersonRoles')
        co_role_ids = []
        for role in co_person_roles:
            role_id = role.get('Id')
            co_role_ids.append(role_id)
            co_person_role = FabricRoles.query.filter_by(role_id=role_id).one_or_none()
            if not co_person_role:
                print("[INFO] Create role for Person: {0}, role: {1}".format(person_uuid, role_id))
                co_person_role = FabricRoles()
                role_found = False
                co_person_role.role_id = role_id
                role_cou = FabricCous.query.filter_by(cou_id=role.get('CouId')).one_or_none()
                if role_cou:
                    role_cou = role_cou.__asdict__()
                    co_person_role.cou_id = role_cou.get('cou_id')
                    co_person_role.role_name = role_cou.get('name')
                else:
                    print("[ERROR] COU for CoPersonRole {0} Not Found -- may need to DELETE role?".format(role_id))
                    continue
            else:
                print("[INFO] Update role for Person: {0}, role: {1}".format(person_uuid, role_id))
                role_found = True
            co_person_role.status = role.get('Status')
            if not role_found:
                db.session.add(co_person_role)
            db.session.commit()

    return True


def get_roles_per_person(person_id: int) -> list:
    people_id = int(person_id)
    roles = []
    fab_roles = FabricRoles.query.filter_by(people_id=people_id).order_by(FabricRoles.role_name).all()
    if fab_roles:
        for r in fab_roles:
            roles.append(r.__asdict__().get('role_name'))

    return roles


def get_projects_per_person(person_id: int) -> list:
    people_id = int(person_id)
    project_cou_id = int(os.getenv('COU_ID_PROJECTS'))
    project_cou_ids = []
    projects = []
    p_cous = FabricCous.query.filter_by(parent_id=project_cou_id).order_by('id')
    for p in p_cous:
        project_cou_ids.append(int(p.__asdict__().get('id')))
    fab_roles = FabricRoles.query.filter(
        FabricRoles.people_id == people_id,
        FabricRoles.cou_id.in_(project_cou_ids)
    ).all()
    if fab_roles:
        p_uuids = []
        for r in fab_roles:
            p_name, p_type = r.__asdict__().get('role_name').rsplit('-', 1)
            if p_name not in p_uuids:
                p_uuids.append(p_name)
        for p_uuid in p_uuids:
            project = FabricProjects.query.filter_by(uuid=p_uuid).one_or_none()
            if project:
                project = project.__asdict__()
                ps = ProjectShort()
                cb = PeopleShort()
                cb_uuid = project.get('created_by')
                cb_person = FabricPeople.query.filter_by(uuid=cb_uuid).one_or_none()
                if cb_person:
                    cb_person = cb_person.__asdict__()
                    cb.email = cb_person.get('email')
                    cb.name = cb_person.get('name')
                    cb.uuid = cb_uuid
                ps.name = project.get('name')
                ps.description = project.get('description')
                ps.uuid = p_uuid
                ps.facility = project.get('facility')
                ps.created_time = project.get('created_time')
                ps.created_by = cb
                projects.append(ps)
        projects = sorted(projects, key=lambda p: p.name, reverse=False)

    return projects
