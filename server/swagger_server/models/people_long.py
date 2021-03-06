# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.project_short import ProjectShort  # noqa: F401,E501
from swagger_server import util


class PeopleLong(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, uuid: str=None, oidc_claim_sub: str=None, name: str=None, email: str=None, roles: List[str]=None, projects: List[ProjectShort]=None):  # noqa: E501
        """PeopleLong - a model defined in Swagger

        :param uuid: The uuid of this PeopleLong.  # noqa: E501
        :type uuid: str
        :param oidc_claim_sub: The oidc_claim_sub of this PeopleLong.  # noqa: E501
        :type oidc_claim_sub: str
        :param name: The name of this PeopleLong.  # noqa: E501
        :type name: str
        :param email: The email of this PeopleLong.  # noqa: E501
        :type email: str
        :param roles: The roles of this PeopleLong.  # noqa: E501
        :type roles: List[str]
        :param projects: The projects of this PeopleLong.  # noqa: E501
        :type projects: List[ProjectShort]
        """
        self.swagger_types = {
            'uuid': str,
            'oidc_claim_sub': str,
            'name': str,
            'email': str,
            'roles': List[str],
            'projects': List[ProjectShort]
        }

        self.attribute_map = {
            'uuid': 'uuid',
            'oidc_claim_sub': 'oidc_claim_sub',
            'name': 'name',
            'email': 'email',
            'roles': 'roles',
            'projects': 'projects'
        }
        self._uuid = uuid
        self._oidc_claim_sub = oidc_claim_sub
        self._name = name
        self._email = email
        self._roles = roles
        self._projects = projects

    @classmethod
    def from_dict(cls, dikt) -> 'PeopleLong':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The People_long of this PeopleLong.  # noqa: E501
        :rtype: PeopleLong
        """
        return util.deserialize_model(dikt, cls)

    @property
    def uuid(self) -> str:
        """Gets the uuid of this PeopleLong.


        :return: The uuid of this PeopleLong.
        :rtype: str
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid: str):
        """Sets the uuid of this PeopleLong.


        :param uuid: The uuid of this PeopleLong.
        :type uuid: str
        """

        self._uuid = uuid

    @property
    def oidc_claim_sub(self) -> str:
        """Gets the oidc_claim_sub of this PeopleLong.


        :return: The oidc_claim_sub of this PeopleLong.
        :rtype: str
        """
        return self._oidc_claim_sub

    @oidc_claim_sub.setter
    def oidc_claim_sub(self, oidc_claim_sub: str):
        """Sets the oidc_claim_sub of this PeopleLong.


        :param oidc_claim_sub: The oidc_claim_sub of this PeopleLong.
        :type oidc_claim_sub: str
        """

        self._oidc_claim_sub = oidc_claim_sub

    @property
    def name(self) -> str:
        """Gets the name of this PeopleLong.


        :return: The name of this PeopleLong.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this PeopleLong.


        :param name: The name of this PeopleLong.
        :type name: str
        """

        self._name = name

    @property
    def email(self) -> str:
        """Gets the email of this PeopleLong.


        :return: The email of this PeopleLong.
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email: str):
        """Sets the email of this PeopleLong.


        :param email: The email of this PeopleLong.
        :type email: str
        """

        self._email = email

    @property
    def roles(self) -> List[str]:
        """Gets the roles of this PeopleLong.


        :return: The roles of this PeopleLong.
        :rtype: List[str]
        """
        return self._roles

    @roles.setter
    def roles(self, roles: List[str]):
        """Sets the roles of this PeopleLong.


        :param roles: The roles of this PeopleLong.
        :type roles: List[str]
        """

        self._roles = roles

    @property
    def projects(self) -> List[ProjectShort]:
        """Gets the projects of this PeopleLong.


        :return: The projects of this PeopleLong.
        :rtype: List[ProjectShort]
        """
        return self._projects

    @projects.setter
    def projects(self, projects: List[ProjectShort]):
        """Sets the projects of this PeopleLong.


        :param projects: The projects of this PeopleLong.
        :type projects: List[ProjectShort]
        """

        self._projects = projects
