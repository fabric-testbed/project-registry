# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.people_long import PeopleLong  # noqa: E501
from swagger_server.models.people_short import PeopleShort  # noqa: E501
from swagger_server.test import BaseTestCase


class TestPeopleController(BaseTestCase):
    """PeopleController integration test stubs"""

    def test_people_get(self):
        """Test case for people_get

        list of people
        """
        query_string = [('person_name', 'person_name_example')]
        headers = [('x_page_no', 'x_page_no_example')]
        response = self.client.open(
            '//people',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_people_oidc_claim_sub_get(self):
        """Test case for people_oidc_claim_sub_get

        person details by OIDC Claim sub
        """
        query_string = [('oidc_claim_sub', 'oidc_claim_sub_example')]
        response = self.client.open(
            '//people/oidc_claim_sub',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_people_uuid_get(self):
        """Test case for people_uuid_get

        person details by UUID
        """
        response = self.client.open(
            '//people/{uuid}'.format(uuid='uuid_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
