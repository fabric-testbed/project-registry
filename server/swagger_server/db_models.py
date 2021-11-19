from datetime import datetime, timezone

from .db import db

"""
TODO: Tables to migrate to new format

- BACKUP:  docker exec -u postgres pr-database sh -c 'pg_dump -Fc postgres > /tmp/backup.sql'
           docker cp pr-database:/tmp/backup.sql ./backup.sql
- RESTORE: docker cp ./backup.sql pr-database:/tmp/backup.sql
           docker exec -u postgres pr-database sh -c \
             'pg_restore -U postgres --data-only -d postgres -t version /tmp/backup.sql'

$ docker exec -u postgres pr-database psql -c '\dt;'
              List of relations
 Schema |      Name       | Type  |  Owner
--------+-----------------+-------+----------
 public | comanage_cous   | table | postgres   # DONE
 public | fabric_people   | table | postgres   # DONE
 public | fabric_projects | table | postgres   # DONE
 public | fabric_roles    | table | postgres   # DONE
 public | project_members | table | postgres   # DONE
 public | project_owners  | table | postgres   # DONE
 public | tags            | table | postgres   # DONE
 public | version         | table | postgres   # DONE
(8 rows)
"""


class ApiVersion(db.Model):
    __tablename__ = 'version'

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(), nullable=False)
    gitsha1 = db.Column(db.String(), nullable=False)

    def __asdict__(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class FabricCous(db.Model):
    __tablename__ = 'comanage_cous'

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(), nullable=False)
    cou_id = db.Column(db.Integer, nullable=False)
    co_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=False)
    parent_id = db.Column(db.Integer, nullable=True)
    lft = db.Column(db.Integer, nullable=True)
    rght = db.Column(db.Integer, nullable=True)
    created_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    modified_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    revision = db.Column(db.Integer, nullable=False)
    deleted = db.Column(db.String(), nullable=False)
    actor_identifier = db.Column(db.String(), nullable=False)

    def __asdict__(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class FabricPeople(db.Model):
    __tablename__ = 'fabric_people'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(), nullable=True)
    oidc_claim_sub = db.Column(db.String(), nullable=False)
    co_person_id = db.Column(db.Integer, nullable=False)
    co_id = db.Column(db.Integer, nullable=False)
    co_status = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)

    def __asdict__(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class FabricProjects(db.Model):
    __tablename__ = 'fabric_projects'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text, nullable=False)
    facility = db.Column(db.String(), nullable=False)
    created_by = db.Column(db.String(), nullable=False)
    created_time = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    modified = db.Column(db.DateTime(timezone=True), onupdate=datetime.now(timezone.utc))

    def __asdict__(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class FabricProjectOwners(db.Model):
    __tablename__ = 'project_owners'

    id = db.Column(db.Integer, primary_key=True)
    projects_id = db.Column(db.Integer, db.ForeignKey('fabric_projects.id'), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey('fabric_people.id'), nullable=False)

    def __asdict__(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class FabricProjectMembers(db.Model):
    __tablename__ = 'project_members'

    id = db.Column(db.Integer, primary_key=True)
    projects_id = db.Column(db.Integer, db.ForeignKey('fabric_projects.id'), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey('fabric_people.id'), nullable=False)

    def __asdict__(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class FabricTags(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    projects_id = db.Column(db.Integer, db.ForeignKey('fabric_projects.id'), nullable=False)
    tag = db.Column(db.Text, nullable=False)

    def __asdict__(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


class FabricRoles(db.Model):
    __tablename__ = 'fabric_roles'

    id = db.Column(db.Integer, primary_key=True)
    people_id = db.Column(db.Integer, db.ForeignKey('fabric_people.id'), nullable=False)
    cou_id = db.Column(db.Integer, db.ForeignKey('comanage_cous.id'), nullable=False)
    role_id = db.Column(db.Integer, nullable=False)
    role_name = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False)

    def __asdict__(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
