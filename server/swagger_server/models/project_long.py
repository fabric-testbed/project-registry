# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.people_short import PeopleShort  # noqa: F401,E501
from swagger_server import util


class ProjectLong(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, uuid: str=None, name: str=None, description: str=None, facility: str=None, tags: List[str]=None, created_time: str=None, created_by: PeopleShort=None, project_owners: List[PeopleShort]=None, project_members: List[PeopleShort]=None):  # noqa: E501
        """ProjectLong - a model defined in Swagger

        :param uuid: The uuid of this ProjectLong.  # noqa: E501
        :type uuid: str
        :param name: The name of this ProjectLong.  # noqa: E501
        :type name: str
        :param description: The description of this ProjectLong.  # noqa: E501
        :type description: str
        :param facility: The facility of this ProjectLong.  # noqa: E501
        :type facility: str
        :param tags: The tags of this ProjectLong.  # noqa: E501
        :type tags: List[str]
        :param created_time: The created_time of this ProjectLong.  # noqa: E501
        :type created_time: str
        :param created_by: The created_by of this ProjectLong.  # noqa: E501
        :type created_by: PeopleShort
        :param project_owners: The project_owners of this ProjectLong.  # noqa: E501
        :type project_owners: List[PeopleShort]
        :param project_members: The project_members of this ProjectLong.  # noqa: E501
        :type project_members: List[PeopleShort]
        """
        self.swagger_types = {
            'uuid': str,
            'name': str,
            'description': str,
            'facility': str,
            'tags': List[str],
            'created_time': str,
            'created_by': PeopleShort,
            'project_owners': List[PeopleShort],
            'project_members': List[PeopleShort]
        }

        self.attribute_map = {
            'uuid': 'uuid',
            'name': 'name',
            'description': 'description',
            'facility': 'facility',
            'tags': 'tags',
            'created_time': 'created_time',
            'created_by': 'created_by',
            'project_owners': 'project_owners',
            'project_members': 'project_members'
        }
        self._uuid = uuid
        self._name = name
        self._description = description
        self._facility = facility
        self._tags = tags
        self._created_time = created_time
        self._created_by = created_by
        self._project_owners = project_owners
        self._project_members = project_members

    @classmethod
    def from_dict(cls, dikt) -> 'ProjectLong':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Project_long of this ProjectLong.  # noqa: E501
        :rtype: ProjectLong
        """
        return util.deserialize_model(dikt, cls)

    @property
    def uuid(self) -> str:
        """Gets the uuid of this ProjectLong.


        :return: The uuid of this ProjectLong.
        :rtype: str
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid: str):
        """Sets the uuid of this ProjectLong.


        :param uuid: The uuid of this ProjectLong.
        :type uuid: str
        """

        self._uuid = uuid

    @property
    def name(self) -> str:
        """Gets the name of this ProjectLong.


        :return: The name of this ProjectLong.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this ProjectLong.


        :param name: The name of this ProjectLong.
        :type name: str
        """

        self._name = name

    @property
    def description(self) -> str:
        """Gets the description of this ProjectLong.


        :return: The description of this ProjectLong.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """Sets the description of this ProjectLong.


        :param description: The description of this ProjectLong.
        :type description: str
        """

        self._description = description

    @property
    def facility(self) -> str:
        """Gets the facility of this ProjectLong.


        :return: The facility of this ProjectLong.
        :rtype: str
        """
        return self._facility

    @facility.setter
    def facility(self, facility: str):
        """Sets the facility of this ProjectLong.


        :param facility: The facility of this ProjectLong.
        :type facility: str
        """

        self._facility = facility

    @property
    def tags(self) -> List[str]:
        """Gets the tags of this ProjectLong.


        :return: The tags of this ProjectLong.
        :rtype: List[str]
        """
        return self._tags

    @tags.setter
    def tags(self, tags: List[str]):
        """Sets the tags of this ProjectLong.


        :param tags: The tags of this ProjectLong.
        :type tags: List[str]
        """

        self._tags = tags

    @property
    def created_time(self) -> str:
        """Gets the created_time of this ProjectLong.


        :return: The created_time of this ProjectLong.
        :rtype: str
        """
        return self._created_time

    @created_time.setter
    def created_time(self, created_time: str):
        """Sets the created_time of this ProjectLong.


        :param created_time: The created_time of this ProjectLong.
        :type created_time: str
        """

        self._created_time = created_time

    @property
    def created_by(self) -> PeopleShort:
        """Gets the created_by of this ProjectLong.


        :return: The created_by of this ProjectLong.
        :rtype: PeopleShort
        """
        return self._created_by

    @created_by.setter
    def created_by(self, created_by: PeopleShort):
        """Sets the created_by of this ProjectLong.


        :param created_by: The created_by of this ProjectLong.
        :type created_by: PeopleShort
        """

        self._created_by = created_by

    @property
    def project_owners(self) -> List[PeopleShort]:
        """Gets the project_owners of this ProjectLong.


        :return: The project_owners of this ProjectLong.
        :rtype: List[PeopleShort]
        """
        return self._project_owners

    @project_owners.setter
    def project_owners(self, project_owners: List[PeopleShort]):
        """Sets the project_owners of this ProjectLong.


        :param project_owners: The project_owners of this ProjectLong.
        :type project_owners: List[PeopleShort]
        """

        self._project_owners = project_owners

    @property
    def project_members(self) -> List[PeopleShort]:
        """Gets the project_members of this ProjectLong.


        :return: The project_members of this ProjectLong.
        :rtype: List[PeopleShort]
        """
        return self._project_members

    @project_members.setter
    def project_members(self, project_members: List[PeopleShort]):
        """Sets the project_members of this ProjectLong.


        :param project_members: The project_members of this ProjectLong.
        :type project_members: List[PeopleShort]
        """

        self._project_members = project_members
