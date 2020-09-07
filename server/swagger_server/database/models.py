# coding: utf-8

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata

FacilityOperators = Table(
    'facility_operators',
    Column('id', Integer, primary_key=True),
    Column('projects_id', Integer, ForeignKey('FabricProjects.id')),
    Column('people_id', Integer, ForeignKey('FabricPeople.id'))
)

ProjectLeads = Table(
    'project_leads',
    Column('id', Integer, primary_key=True),
    Column('projects_id', Integer, ForeignKey('FabricProjects.id')),
    Column('people_id', Integer, ForeignKey('FabricPeople.id'))
)

ProjectOwners = Table(
    'project_owners',
    Column('id', Integer, primary_key=True),
    Column('projects_id', Integer, ForeignKey('FabricProjects.id')),
    Column('people_id', Integer, ForeignKey('FabricPeople.id'))
)

ProjectMembers = Table(
    'project_members',
    Column('id', Integer, primary_key=True),
    Column('projects_id', Integer, ForeignKey('FabricProjects.id')),
    Column('people_id', Integer, ForeignKey('FabricPeople.id'))
)

ProjectTags = Table(
    'tags',
    Column('id', Integer, primary_key=True),
    Column('projects_id', Integer, ForeignKey('FabricProjects.id')),
    Column('tag_id', Integer, ForeignKey('FabricTags.id'))
)


class FabricProjects(Base):
    """
    FABRIC Project information
    """
    __tablename__ = 'fabric_projects'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    uuid = Column(String)
    cou = Column(String)
    facility = Column(String)
    facility_operators = relationship('FabricPeople', secondary=FacilityOperators, backref='FabricProjects')
    project_leads = relationship('FabricPeople', secondary=ProjectLeads, backref='FabricProjects')
    project_owners = relationship('FabricPeople', secondary=ProjectOwners, backref='FabricProjects')
    project_members = relationship('FabricPeople', secondary=ProjectMembers, backref='FabricProjects')
    tags = relationship('FabricTags', secondary=ProjectTags, backref='FabricProjects')


class FabricPeople(Base):
    """
    FABRIC People information
    """
    __tablename__ = 'fabric_people'

    id = Column(Integer, primary_key=True)
    uuid = Column(String)
    cilogon_id = Column(String)
    name = Column(String)
    email = Column(String)
    eppn = Column(String)


class FabricTags(Base):
    """
    FABRIC Tags information
    """
    __tablename__ = 'fabric_tags'

    id = Column(Integer, primary_key=True)
    uuid = Column(String)
    tag = Column(String)
    description = Column(String)


class Version(Base):
    """
    FABRIC API Version information
    """
    __tablename__ = 'version'

    id = Column(Integer, primary_key=True)
    version = Column(String)
    gitsha1 = Column(String)
