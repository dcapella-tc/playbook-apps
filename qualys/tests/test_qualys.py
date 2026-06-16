import unittest
from unittest.mock import MagicMock, patch

import requests

from helpers.qualys import get_qualys_cve_data


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


if __name__ == '__main__':
    unittest.main()
