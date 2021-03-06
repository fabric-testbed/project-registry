#!/usr/bin/env python3

from configparser import ConfigParser

import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

config = ConfigParser()
config.read('../server/swagger_server/config/config.ini')

POSTGRES_ENGINE = 'postgres://' + config.get('postgres', 'user') + ':' + config.get('postgres', 'password') \
                  + '@' + config.get('postgres', 'host') + ':' + config.get('postgres', 'port') \
                  + '/' + config.get('postgres', 'database')

engine = create_engine(POSTGRES_ENGINE)
Session = sessionmaker(bind=engine)


def create_tables():
    """ create tables in the PostgreSQL database"""
    commands = (
        """
        DROP TABLE IF EXISTS fabric_projects CASCADE 
        """,
        """
        CREATE TABLE fabric_projects (
            id SERIAL PRIMARY KEY,
            uuid VARCHAR(36) NOT NULL,
            name VARCHAR(255) NOT NULL,
            description VARCHAR(2083) NOT NULL,
            facility VARCHAR(255) NOT NULL,
            created_by VARCHAR(36) NOT NULL,
            created_time VARCHAR(255) NOT NULL,
            CONSTRAINT projects_uuid UNIQUE (uuid)
        )
        """,
        """
        DROP TABLE IF EXISTS fabric_people CASCADE 
        """,
        """
        CREATE TABLE fabric_people (
            id SERIAL PRIMARY KEY,
            uuid VARCHAR(36) NOT NULL,
            oidc_claim_sub VARCHAR(255) NOT NULL,
            co_person_id INTEGER NOT NULL,
            co_id INTEGER NOT NULL,
            co_status VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            CONSTRAINT actor_identifier_duplicate UNIQUE (oidc_claim_sub)
        )
        """,
        """
        DROP TABLE IF EXISTS version CASCADE 
        """,
        """
        CREATE TABLE version (
            id SERIAL PRIMARY KEY,
            version VARCHAR(255) NOT NULL,
            gitsha1 VARCHAR(255) NOT NULL
        )
        """,
        """
        DROP TABLE IF EXISTS project_owners CASCADE 
        """,
        """
        CREATE TABLE project_owners (
            id SERIAL PRIMARY KEY,
            projects_id int NOT NULL,
            people_id int NOT NULL,
            FOREIGN KEY (projects_id) REFERENCES fabric_projects(id) ON UPDATE CASCADE,
            FOREIGN KEY (people_id) REFERENCES fabric_people(id) ON UPDATE CASCADE,
            CONSTRAINT project_owners_duplicate UNIQUE (projects_id, people_id) 
        )
        """,
        """
        DROP TABLE IF EXISTS project_members CASCADE 
        """,
        """
        CREATE TABLE project_members (
            id SERIAL PRIMARY KEY,
            projects_id int NOT NULL,
            people_id int NOT NULL,
            FOREIGN KEY (projects_id) REFERENCES fabric_projects(id) ON UPDATE CASCADE,
            FOREIGN KEY (people_id) REFERENCES fabric_people(id) ON UPDATE CASCADE,
            CONSTRAINT project_members_duplicate UNIQUE (projects_id, people_id) 
        )
        """,
        """
        DROP TABLE IF EXISTS tags CASCADE 
        """,
        """
        CREATE TABLE tags (
            id SERIAL PRIMARY KEY,
            projects_id int NOT NULL,
            tag VARCHAR(255) NOT NULL,
            FOREIGN KEY (projects_id) REFERENCES fabric_projects(id) ON UPDATE CASCADE,
            CONSTRAINT tags_duplicate UNIQUE (projects_id, tag)  
        )
        """,
        """
        DROP TABLE IF EXISTS comanage_cous CASCADE 
        """,
        """
        CREATE TABLE comanage_cous (
            id SERIAL PRIMARY KEY,
            version VARCHAR(255) NOT NULL,
            cou_id INTEGER NOT NULL,
            co_id INTEGER NOT NULL,
            name VARCHAR(255) NOT NULL,
            description VARCHAR(255) NOT NULL,
            parent_id INTEGER,
            lft INTEGER,
            rght INTEGER,
            created_date VARCHAR(255) NOT NULL,
            modified_date VARCHAR(255) NOT NULL,
            revision INTEGER NOT NULL,
            deleted VARCHAR(255) NOT NULL,
            actor_identifier VARCHAR(255) NOT NULL,
            CONSTRAINT cou_id_duplicate UNIQUE (cou_id)
        )
        """,
        """
        DROP TABLE IF EXISTS fabric_roles CASCADE 
        """,
        """
        CREATE TABLE fabric_roles (
            id SERIAL PRIMARY KEY,
            people_id int NOT NULL,
            cou_id int NOT NULL,
            role_id int NOT NULL,
            role_name VARCHAR(255) NOT NULL,
            FOREIGN KEY (people_id) REFERENCES fabric_people(id) ON UPDATE CASCADE,
            FOREIGN KEY (cou_id) REFERENCES comanage_cous(id) ON UPDATE CASCADE,
            CONSTRAINT fabric_role_duplicate UNIQUE (people_id, cou_id)  
        )
        """
    )

    session = Session()
    try:
        # create table one by one
        for command in commands:
            session.execute(command)
        session.commit()
        print("[INFO] tables created successfully!")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if session is not None:
            session.close()


if __name__ == '__main__':
    create_tables()
