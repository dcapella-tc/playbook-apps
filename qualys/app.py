"""ThreatConnect Playbook App"""

import requests
from tcex import TcEx
from tcex.exit import ExitCode

from helpers.qualys import get_qualys_cve_data, get_qualys_token
from playbook_app import PlaybookApp  # Import default Playbook App Class (Required)


class App(PlaybookApp):
    """Playbook App"""

    def __init__(self, _tcex: TcEx):
        """Initialize class properties.

        This method can be OPTIONALLY overridden.
        """
        super().__init__(_tcex)
        self.qualys_cve_data: str

    def run(self):
        """Run the App main logic.

        This method should contain the core logic of the App.
        """
        try:
            token = get_qualys_token(
                self.in_.qualys_base_url,
                self.in_.qualys_username,
                self.in_.qualys_api_key,
            )
            self.qualys_cve_data = get_qualys_cve_data(
                self.in_.qualys_base_url,
                token,
                self.in_.cve,
            )
        except requests.HTTPError:
            self.log.exception('Qualys API request failed.')
            self.tcex.exit.exit(ExitCode.FAILURE, 'Qualys API request failed.')
        except requests.RequestException:
            self.log.exception('Qualys API connection error.')
            self.tcex.exit.exit(ExitCode.FAILURE, 'Qualys API connection error.')

        self.exit_message = f'Qualys CVE data retrieved for {self.in_.cve}.'

    def write_output(self):
        """Write the Playbook output variables.

        This method should be overridden with the output variables defined in the install.json
        configuration file.
        """
        self.log.info('Writing Output')
        self.playbook.create.string('qualys.cve.data', self.qualys_cve_data)
