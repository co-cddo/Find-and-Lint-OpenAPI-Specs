import os
import unittest
from unittest import mock
from unittest.mock import Mock, patch

from find_and_lint_openapi_docs import convert_to_raw_content_url, is_an_archived_repository, get_api_name, \
    get_api_description, get_organisation_name, get_api_version, get_last_commit_date


class FindAndLintOpenApiDocsTestCase(unittest.TestCase):

    def test_convert_to_raw_content_url(self):
        result = convert_to_raw_content_url(
            'https://github.com/alphagov/tech-docs-gem/blob/8aefa0d5a2b05f74ab3e50f6576035344672a376/example/source'
            '/pets.yml')

        self.assertEqual(
            'https://raw.githubusercontent.com/alphagov/tech-docs-gem/8aefa0d5a2b05f74ab3e50f6576035344672a376'
            '/example/source/pets.yml',
            result)

    @mock.patch.dict(os.environ, {"USERNAME": "test_username", "API_TOKEN": "test_token"})
    @patch('find_and_lint_openapi_docs.requests.get')
    def test_is_an_archived_repository(self, mock_get):
        item = {'repository': {'full_name': 'test_name'}}
        mock_result = {'archived': True}
        mock_get.return_value = Mock()
        mock_get.return_value.json.return_value = mock_result

        result = is_an_archived_repository(item)

        self.assertTrue(result)

    @mock.patch.dict(os.environ, {"USERNAME": "test_username", "API_TOKEN": "test_token"})
    @patch('find_and_lint_openapi_docs.requests.get')
    def test_is_not_an_archived_repository(self, mock_get):
        item = {'repository': {'full_name': 'test_name'}}
        mock_result = {'archived': False}
        mock_get.return_value = Mock()
        mock_get.return_value.json.return_value = mock_result

        result = is_an_archived_repository(item)

        self.assertFalse(result)

    def test_get_api_name(self):
        info_object = {'version': '1.0.0', 'title': 'Test title', 'description': 'Test description',
                       'license': {'name': 'MIT'}}

        result = get_api_name(info_object)

        self.assertEqual('Test title', result)

    def test_get_api_name_from_file_without_title_field(self):
        info_object = {'version': '1.0.0', 'description': 'Test description', 'license': {'name': 'MIT'}}

        result = get_api_name(info_object)

        self.assertEqual('N/A', result)

    def test_get_api_description(self):
        info_object = {'version': '1.0.0', 'title': 'Test title',
                       'description': 'Test description.\n It has multiple lines.', 'license': {'name': 'MIT'}}

        result = get_api_description(info_object)

        self.assertEqual('Test description.', result)

    def test_get_api_description_from_file_without_description_field(self):
        info_object = {'version': '1.0.0', 'title': 'Test title', 'license': {'name': 'MIT'}}

        result = get_api_description(info_object)

        self.assertEqual('N/A', result)

    def test_get_api_version_from_file(self):
        info_object = {'version': '1.0.0', 'title': 'Test title', 'license': {'name': 'MIT'}}

        result = get_api_version(info_object)

        self.assertEqual('1.0.0', result)

    def test_get_api_version_from_file_without_version(self):
        info_object = {'title': 'Test title', 'license': {'name': 'MIT'}}

        result = get_api_version(info_object)

        self.assertEqual('N/A', result)

    @mock.patch.dict(os.environ, {"USERNAME": "test_username", "API_TOKEN": "test_token"})
    @patch('find_and_lint_openapi_docs.requests.get')
    def test_get_organisation_name(self, mock_get):
        mock_get.return_value.json.return_value = {'login': 'test-org', 'name': 'Test Organisation'}

        result = get_organisation_name('test-org')

        self.assertEqual('Test Organisation', result)

    @mock.patch.dict(os.environ, {"USERNAME": "test_username", "API_TOKEN": "test_token"})
    @patch('find_and_lint_openapi_docs.requests.get')
    def test_get_last_updated(self, mock_get):
        item = {'repository': {'full_name': 'test_name'}}
        mock_get.return_value.json.return_value = [{'commit': {'committer': {'date': '2022-05-16T10:17:54Z'}}}]

        result = get_last_commit_date(item)

        self.assertEqual('2022-05-16T10:17:54Z', result)
