import unittest
from unittest.mock import MagicMock, patch

import requests

from helpers.qualys import get_qualys_cve_data, get_qualys_token, qualys_gateway_url


class TestQualysGatewayUrl(unittest.TestCase):
    def test_platform_3(self):
        self.assertEqual(
            qualys_gateway_url('https://qualysapi.qg3.apps.qualys.com'),
            'https://gateway.qg3.apps.qualys.com',
        )

    def test_platform_1(self):
        self.assertEqual(
            qualys_gateway_url('https://qualysapi.qualys.com/'),
            'https://gateway.qualys.com',
        )

    def test_strips_trailing_slash(self):
        self.assertEqual(
            qualys_gateway_url('https://qualysapi.qg3.apps.qualys.com///'),
            'https://gateway.qg3.apps.qualys.com',
        )

    def test_already_gateway_unchanged(self):
        url = 'https://gateway.qg3.apps.qualys.com'
        self.assertEqual(qualys_gateway_url(url), url)


class TestGetQualysCveData(unittest.TestCase):
    @patch('helpers.qualys.requests.post')
    def test_success(self, mock_post: MagicMock):
        mock_response = MagicMock()
        mock_response.text = '<VULN_LIST></VULN_LIST>'
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = get_qualys_cve_data(
            'https://qualysapi.qualys.com/',
            'test-jwt',
            'CVE-2024-1234',
        )

        self.assertEqual(result, '<VULN_LIST></VULN_LIST>')
        mock_post.assert_called_once_with(
            'https://qualysapi.qualys.com/api/4.0/fo/knowledge_base/vuln/',
            headers={
                'X-Requested-With': 'curl',
                'Authorization': 'Bearer test-jwt',
            },
            params={'action': 'list', 'cve': 'CVE-2024-1234'},
            timeout=60,
        )

    @patch('helpers.qualys.requests.post')
    def test_strips_trailing_slash_from_base_url(self, mock_post: MagicMock):
        mock_response = MagicMock()
        mock_response.text = 'ok'
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        get_qualys_cve_data('https://qualysapi.qualys.com///', 'token', 'CVE-2024-1')

        mock_post.assert_called_once()
        self.assertEqual(
            mock_post.call_args.args[0],
            'https://qualysapi.qualys.com/api/4.0/fo/knowledge_base/vuln/',
        )

    @patch('helpers.qualys.requests.post')
    def test_http_error_raises(self, mock_post: MagicMock):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError('401 Client Error')
        mock_post.return_value = mock_response

        with self.assertRaises(requests.HTTPError):
            get_qualys_cve_data('https://qualysapi.qualys.com', 'bad-token', 'CVE-2024-1234')


class TestGetQualysToken(unittest.TestCase):
    @patch('helpers.qualys.requests.post')
    def test_success(self, mock_post: MagicMock):
        mock_response = MagicMock()
        mock_response.text = '  test-jwt-token  '
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        result = get_qualys_token(
            'https://qualysapi.qualys.com/',
            'theat3dw',
            'secret-api-key',
        )

        self.assertEqual(result, 'test-jwt-token')
        mock_post.assert_called_once_with(
            'https://gateway.qualys.com/auth',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'Python requests',
            },
            data={
                'username': 'theat3dw',
                'password': 'secret-api-key',
                'token': 'true',
            },
            timeout=30,
        )

    @patch('helpers.qualys.requests.post')
    def test_platform_3_uses_gateway_host(self, mock_post: MagicMock):
        mock_response = MagicMock()
        mock_response.text = 'jwt'
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        get_qualys_token('https://qualysapi.qg3.apps.qualys.com', 'user', 'key')

        self.assertEqual(
            mock_post.call_args.args[0],
            'https://gateway.qg3.apps.qualys.com/auth',
        )

    @patch('helpers.qualys.requests.post')
    def test_strips_trailing_slash_from_base_url(self, mock_post: MagicMock):
        mock_response = MagicMock()
        mock_response.text = 'token'
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        get_qualys_token('https://qualysapi.qualys.com///', 'user', 'key')

        mock_post.assert_called_once()
        self.assertEqual(mock_post.call_args.args[0], 'https://gateway.qualys.com/auth')

    @patch('helpers.qualys.requests.post')
    def test_http_error_raises(self, mock_post: MagicMock):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError('401 Client Error')
        mock_post.return_value = mock_response

        with self.assertRaises(requests.HTTPError):
            get_qualys_token('https://qualysapi.qualys.com', 'user', 'bad-key')


if __name__ == '__main__':
    unittest.main()
