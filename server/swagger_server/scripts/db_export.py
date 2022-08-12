"""
PR to fabric-core-api migration
- People
    - co_person_id
    - uuid (compare to UIS)
- Projects
    - description
    - tags
- Tags

$ docker exec -u postgres pr-database psql -c "\dt;"
              List of relations
 Schema |      Name       | Type  |  Owner
--------+-----------------+-------+----------
 public | alembic_version | table | postgres
 public | comanage_cous   | table | postgres
 public | fabric_people   | table | postgres
 public | fabric_projects | table | postgres
 public | fabric_roles    | table | postgres
 public | project_members | table | postgres
 public | project_owners  | table | postgres
 public | tags            | table | postgres
 public | version         | table | postgres
"""

import json
import logging

from swagger_server.__main__ import create_app
from swagger_server.db_models import FabricProjects, FabricPeople, FabricTags

logger = logging.getLogger(__file__)


# export projects as JSON object
def dump_projects_data():
    """
    Projects
    - id = db.Column(db.Integer, primary_key=True)
    - uuid = db.Column(db.String(), nullable=False)
    - name = db.Column(db.String(), nullable=False)
    - description = db.Column(db.Text, nullable=False)
    - facility = db.Column(db.String(), nullable=False)
    - created_by = db.Column(db.String(), nullable=False)
    - created_time = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - modified = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    """
    projects = []
    fab_projects = FabricProjects.query.order_by('id').all()
    for p in fab_projects:
        data = {
            'id': p.id,
            'uuid': p.uuid,
            'name': p.name,
            'description': p.description,
            'facility': p.facility,
            'created_by': p.created_by,
            'created_time': str(p.created_time),
            'modified': str(p.modified)
        }
        projects.append(data)
    output_dict = {'pr_projects': projects}
    output_json = json.dumps(output_dict, indent=2)
    print(json.dumps(output_dict, indent=2))
    with open("pr_projects.json", "w") as outfile:
        outfile.write(output_json)


# export people as JSON object
def dump_people_data():
    """
    People
    - id = db.Column(db.Integer, primary_key=True)
    - uuid = db.Column(db.String(), nullable=True)
    - oidc_claim_sub = db.Column(db.String(), nullable=False)
    - co_person_id = db.Column(db.Integer, nullable=False)
    - co_id = db.Column(db.Integer, nullable=False)
    - co_status = db.Column(db.String(), nullable=False)
    - name = db.Column(db.String(), nullable=False)
    - email = db.Column(db.String(), nullable=False)
    """
    people = []
    fab_people = FabricPeople.query.order_by('id').all()
    for p in fab_people:
        data = {
            'id': p.id,
            'uuid': p.uuid,
            'oidc_claim_sub': p.oidc_claim_sub,
            'co_person_id': p.co_person_id,
            'co_id': p.co_id,
            'co_status': p.co_status,
            'name': p.name,
            'email': p.email
        }
        people.append(data)
    output_dict = {'pr_people': people}
    output_json = json.dumps(output_dict, indent=2)
    print(json.dumps(output_dict, indent=2))
    with open("pr_people.json", "w") as outfile:
        outfile.write(output_json)


def dump_tags_data():
    """
    id = db.Column(db.Integer, primary_key=True)
    projects_id = db.Column(db.Integer, db.ForeignKey('fabric_projects.id'), nullable=False)
    tag = db.Column(db.Text, nullable=False)
    """
    tags = []
    fab_tags = FabricTags.query.order_by('id').all()
    for p in fab_tags:
        data = {
            'id': p.id,
            'projects_id': p.id,
            'tag': p.id
        }
        tags.append(data)
    output_dict = {'pr_tags': tags}
    output_json = json.dumps(output_dict, indent=2)
    print(json.dumps(output_dict, indent=2))
    with open("pr_tags.json", "w") as outfile:
        outfile.write(output_json)


if __name__ == '__main__':
    app = create_app()
    app.app_context().push()
    logger.info("dump projects table")
    dump_projects_data()
    logger.info("dump people table")
    dump_people_data()
    logger.info("dump tags table")
    dump_tags_data()
