# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.project_long import ProjectLong  # noqa: E501
from swagger_server.models.project_short import ProjectShort  # noqa: E501
from swagger_server.test import BaseTestCase


class TestProjectsController(BaseTestCase):
    """ProjectsController integration test stubs"""

    def test_projects_add_members_put(self):
        """Test case for projects_add_members_put

        add members to an existing project
        """
        query_string = [('project_id', 'project_id_example'),
                        ('project_members', 'project_members_example')]
        response = self.client.open(
            '//projects/add_members',
            method='PUT',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_add_owners_put(self):
        """Test case for projects_add_owners_put

        add owners to an existing project
        """
        query_string = [('project_id', 'project_id_example'),
                        ('project_owners', 'project_owners_example')]
        response = self.client.open(
            '//projects/add_owners',
            method='PUT',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_add_tags_put(self):
        """Test case for projects_add_tags_put

        add tags to an existing project
        """
        query_string = [('project_id', 'project_id_example'),
                        ('tags', 'tags_example')]
        response = self.client.open(
            '//projects/add_tags',
            method='PUT',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_create_post(self):
        """Test case for projects_create_post

        create new project
        """
        query_string = [('name', 'name_example'),
                        ('description', 'description_example'),
                        ('facility', 'facility_example'),
                        ('tags', 'tags_example'),
                        ('project_owners', 'project_owners_example'),
                        ('project_members', 'project_members_example')]
        response = self.client.open(
            '//projects/create',
            method='POST',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_delete_delete(self):
        """Test case for projects_delete_delete

        delete existing project
        """
        query_string = [('project_id', 'project_id_example')]
        response = self.client.open(
            '//projects/delete',
            method='DELETE',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_get(self):
        """Test case for projects_get

        list of projects
        """
        response = self.client.open(
            '//projects',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_project_idget(self):
        """Test case for projects_project_idget

        project details
        """
        response = self.client.open(
            '//projects/{PROJECT_ID}'.format(project_id='project_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_remove_members_put(self):
        """Test case for projects_remove_members_put

        remove members to an existing project
        """
        query_string = [('project_id', 'project_id_example'),
                        ('project_members', 'project_members_example')]
        response = self.client.open(
            '//projects/remove_members',
            method='PUT',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_remove_owners_put(self):
        """Test case for projects_remove_owners_put

        remove owners to an existing project
        """
        query_string = [('project_id', 'project_id_example'),
                        ('project_owners', 'project_owners_example')]
        response = self.client.open(
            '//projects/remove_owners',
            method='PUT',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_remove_tags_put(self):
        """Test case for projects_remove_tags_put

        remove tags to an existing project
        """
        query_string = [('project_id', 'project_id_example'),
                        ('tags', 'tags_example')]
        response = self.client.open(
            '//projects/remove_tags',
            method='PUT',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_update_put(self):
        """Test case for projects_update_put

        update an existing project
        """
        query_string = [('project_id', 'project_id_example'),
                        ('name', 'name_example'),
                        ('description', 'description_example'),
                        ('facility', 'facility_example')]
        response = self.client.open(
            '//projects/update',
            method='PUT',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
