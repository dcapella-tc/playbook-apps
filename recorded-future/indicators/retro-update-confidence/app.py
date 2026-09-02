"""ThreatConnect Exchange Playbook App"""

from __future__ import annotations

from itertools import islice
from typing import Any

import requests
from tcex import TcEx
from tcex.exit import ExitCode

from helpers.indicators import (
    RESULT_LIMIT,
    iter_indicators,
    risk_score_confidence,
    update_confidence,
)
from playbook_app import PlaybookApp


class App(PlaybookApp):
    """ThreatConnect Exchange App"""

    def __init__(self, _tcex: TcEx):
        """Initialize class properties."""
        super().__init__(_tcex)
        self.updated_count: int = 0
        self.skipped_count: int = 0
        self.failed_count: int = 0

    def run(self):
        """Run the App main logic.

        Retrieve TQL-matched indicators and set confidence from Risk Score.
        """
        tql = str(self.in_.tql or '').strip()
        if not tql:
            self.tcex.exit.exit(ExitCode.FAILURE, 'TQL input is required.')

        limit = int(self.in_.limit)
        page_size = min(limit, RESULT_LIMIT)

        try:
            with self.tcex.session.tc as session:
                for indicator in islice(
                    iter_indicators(session, tql, result_limit=page_size),
                    limit,
                ):
                    self._update_indicator(session, indicator)
        except requests.RequestException as exc:
            self.log.exception('Failed to retrieve indicators.')
            self.tcex.exit.exit(ExitCode.FAILURE, f'Failed to retrieve indicators: {exc}')

        self.exit_message = (
            f'Updated {self.updated_count} indicators '
            f'({self.skipped_count} skipped, {self.failed_count} failed).'
        )

    def _update_indicator(self, session: requests.Session, indicator: dict[str, Any]) -> None:
        """Update one indicator's confidence from its Risk Score attribute."""
        indicator_id = indicator.get('id')
        summary = indicator.get('summary', indicator_id)
        confidence = risk_score_confidence(indicator)
        if confidence is None:
            self.log.info(
                'Skipping indicator %s: missing or invalid Risk Score attribute',
                summary,
            )
            self.skipped_count += 1
            return

        if indicator.get('confidence') == confidence:
            self.log.info(
                'Skipping indicator %s: confidence already %s',
                summary,
                confidence,
            )
            self.skipped_count += 1
            return

        if indicator_id is None:
            self.log.error('Failed to update indicator %s: missing id', summary)
            self.failed_count += 1
            return

        try:
            update_confidence(session, indicator_id, confidence)
        except requests.RequestException:
            self.log.exception('Failed to update indicator %s', summary)
            self.failed_count += 1
            return

        self.updated_count += 1

    def write_output(self):
        """Write the Playbook output variables."""
        self.log.info('Writing Output')
        self.playbook.create.string('indicators.updated', self.updated_count)
        self.playbook.create.string('indicators.skipped', self.skipped_count)
        self.playbook.create.string('indicators.failed', self.failed_count)
