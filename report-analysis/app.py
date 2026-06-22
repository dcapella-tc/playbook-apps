"""ThreatConnect Exchange Playbook App"""

from typing import cast

from tcex import TcEx
from tcex.exit import ExitCode

from helpers.doc_analysis import doc_analysis
from helpers.jmespath_indicator import jmespath_indicator
from helpers.jmespath_postprocess import jmespath_postprocess
from helpers.jmespath_preprocess import jmespath_preprocess
from helpers.tc_create_indicator import create_indicator
from helpers.tc_create_report import create_report
from helpers.tc_update_report import update_report
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
            preprocessed = jmespath_preprocess(content)
            analyzed = doc_analysis(preprocessed)
            report_payload = jmespath_postprocess(analyzed)
            report = create_report(
                self.tcex,
                self.in_.owner_name,
                self.in_.report_name,
                report_payload,
            )
            update_report(
                self.tcex,
                self.in_.owner_name,
                report,
                report_payload,
            )

            for indicator_raw in report_payload.get('indicators', []):
                indicator_data = jmespath_indicator(indicator_raw)
                create_indicator(
                    self.tcex,
                    self.in_.owner_name,
                    indicator_data,
                    report['xid'],
                )
        except ValueError as exc:
            self.log.exception('Report analysis failed.')
            self.tcex.exit.exit(ExitCode.FAILURE, str(exc))

        self.exit_message = f'Report {self.in_.report_name} processed.'

    def write_output(self):
        """Write the Playbook output variables.

        This method should be overridden with the output variables defined in the install.json
        configuration file.
        """
