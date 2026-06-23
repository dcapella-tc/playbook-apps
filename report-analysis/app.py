"""ThreatConnect Exchange Playbook App"""

from typing import cast

import requests
from tcex import TcEx
from tcex.exit import ExitCode

from helpers.doc_analysis import doc_analysis
from helpers.enrich_report import enrich_report
from helpers.tc_create_report import create_report
from playbook_app import PlaybookApp


class App(PlaybookApp):
    """ThreatConnect Exchange App"""

    def __init__(self, _tcex: TcEx):
        """Initialize class properties."""
        super().__init__(_tcex)
        self.batch = self.tcex.api.tc.v2.batch(self.in_.owner_name)

    def run(self):
        """Run the App main logic.

        This method should contain the core logic of the App.
        """
        try:
            content = cast('str', self.in_unresolved.content)
            with self.tcex.session.external as session:
                analysis = doc_analysis(
                    content,
                    session=session,
                    cal_host=self.in_.tc_cal_host,
                    cal_token=str(self.in_.tc_cal_token),
                    cal_timestamp=self.in_.tc_cal_timestamp,
                    resolve_mitre_tag=self.tcex.api.tc.v3.mitre_tags.get_by_id,
                )
            report = create_report(
                self.batch,
                self.in_.owner_name,
                self.in_.report_name,
            )
            enrich_report(
                self.batch,
                self.in_.owner_name,
                report,
                analysis,
            )

            batch_response = self.batch.submit_all()
            self.batch.close()

            errors: list = []
            successes: list = []
            for item in batch_response:
                errors.extend(item.get('errors', []))
                successes.extend(item.get('successes', []))

            if errors:
                self.log.error('Batch submission failed with %d errors', len(errors))
                self.tcex.exit.exit(ExitCode.FAILURE, f'Batch submission failed: {errors[0]}')

            if successes:
                self.log.info('Batch submission successful with %d items', len(successes))
        except ValueError as exc:
            self.log.exception('Report analysis failed.')
            self.tcex.exit.exit(ExitCode.FAILURE, str(exc))
        except requests.RequestException as exc:
            self.log.exception('CAL request failed.')
            self.tcex.exit.exit(ExitCode.FAILURE, f'CAL request failed: {exc}')

        self.exit_message = f'Report {self.in_.report_name} processed.'

    def write_output(self):
        """Write the Playbook output variables.

        This method should be overridden with the output variables defined in the install.json
        configuration file.
        """
