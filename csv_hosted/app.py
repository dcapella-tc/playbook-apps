"""ThreatConnect Playbook App"""

import os
from pathlib import Path
from typing import cast

from tcex import TcEx

from playbook_app import PlaybookApp  # Import default Playbook App Class (Required)


class App(PlaybookApp):
    """Playbook App: publish CSV text to ThreatConnect fileshare (data.csv)."""

    def __init__(self, _tcex: TcEx):
        """Initialize class properties.

        This method can be OPTIONALLY overridden.
        """
        super().__init__(_tcex)

    def run(self):
        """Run the App main logic.

        This method should contain the core logic of the App.
        """
        csv_text = self._resolve_csv_text()
        out_dir = self._resolve_output_dir()
        out_path = out_dir / 'data.csv'
        out_path.write_text(csv_text, encoding='utf-8', newline='')

        self.exit_message = 'CSV written to fileshare output.'

    def _resolve_csv_text(self) -> str:
        """Return CSV body as a single string (opaque; no parsing)."""
        raw = cast('str', self.in_unresolved.csv_data)  # type: ignore[attr-defined]
        if self.playbook.get_variable_type(raw) == 'String':
            return cast('str', self.in_.csv_data)
        return str(self.in_.csv_data)

    def _resolve_output_dir(self) -> Path:
        """Directory where publishOutFiles must be written (SDK / platform naming varies)."""
        for attr in ('tc_out_path', 'tc_output_path'):
            val = getattr(self.in_, attr, None)
            if val:
                return Path(str(val))
        for env_key in ('TC_OUTPUT_PATH', 'TC_OUT_PATH'):
            val = os.environ.get(env_key)
            if val:
                return Path(val)
        self.tcex.exit.exit(
            1,
            'Could not resolve ThreatConnect output directory for fileshare '
            '(expected tc_out_path / tc_output_path on inputs or TC_OUTPUT_PATH / TC_OUT_PATH).',
        )
        msg = 'TcEx exit did not terminate after fatal error.'
        raise RuntimeError(msg)

    def write_output(self):
        """Write the Playbook output variables.

        This method should be overridden with the output variables defined in the install.json
        configuration file.
        """
        self.log.info('Writing Output')
        self.playbook.create.string('csv.filename', 'data.csv')
