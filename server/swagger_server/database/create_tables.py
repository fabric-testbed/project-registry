#!/usr/bin/env python3
import sys

import psycopg2

sys.path.append("..")

from database import Session


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
            description VARCHAR(255) NOT NULL,
            cou VARCHAR(255) NOT NULL,
            facility VARCHAR(255) NOT NULL,
            CONSTRAINT projects_cou UNIQUE (cou)
        )
        """,
        """
        DROP TABLE IF EXISTS fabric_people CASCADE 
        """,
        """
        CREATE TABLE fabric_people (
            id SERIAL PRIMARY KEY,
            uuid VARCHAR(36) NOT NULL,
            cilogon_id VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            eppn VARCHAR(255) NOT NULL,
            is_facility_operator BOOLEAN NOT NULL,
            is_project_lead BOOLEAN NOT NULL,
            CONSTRAINT cilogon_uid UNIQUE (cilogon_id)
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
        DROP TABLE IF EXISTS facility_operators CASCADE 
        """,
        """
        CREATE TABLE facility_operators (
            id SERIAL PRIMARY KEY,
            projects_id int NOT NULL,
            people_id int NOT NULL,
            FOREIGN KEY (projects_id) REFERENCES fabric_projects(id) ON UPDATE CASCADE,
            FOREIGN KEY (people_id) REFERENCES fabric_people(id) ON UPDATE CASCADE,
            CONSTRAINT facility_operators_duplicate UNIQUE (projects_id, people_id) 
        )
        """,
        """
        DROP TABLE IF EXISTS project_leads CASCADE 
        """,
        """
        CREATE TABLE project_leads (
            id SERIAL PRIMARY KEY,
            projects_id int NOT NULL,
            people_id int NOT NULL,
            FOREIGN KEY (projects_id) REFERENCES fabric_projects(id) ON UPDATE CASCADE,
            FOREIGN KEY (people_id) REFERENCES fabric_people(id) ON UPDATE CASCADE,
            CONSTRAINT project_leads_duplicate UNIQUE (projects_id, people_id) 
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
        DROP TABLE IF EXISTS roles CASCADE 
        """,
        """
        CREATE TABLE roles (
            id SERIAL PRIMARY KEY,
            people_id int NOT NULL,
            role VARCHAR(255) NOT NULL,
            FOREIGN KEY (people_id) REFERENCES fabric_people(id) ON UPDATE CASCADE,
            CONSTRAINT roles_duplicate UNIQUE (people_id, role)  
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
