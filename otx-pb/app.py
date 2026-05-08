"""ThreatConnect Exchange Playbook App"""

from playbook_app import PlaybookApp

import re
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional, Union
from uuid import uuid5, NAMESPACE_URL
import json
from tcex import TcEx
from tcex.exit import ExitCode

from naics import naics_tags_for_keyword

# Match "N Days Ago" or "N Day Ago" (case-insensitive)
_DAYS_AGO_RE = re.compile(r'^\s*(\d+)\s+days?\s+ago\s*$', re.IGNORECASE)


def parse_last_run(value: str) -> datetime:
    """Convert last_run string to a UTC datetime.

    Accepts:
        - "N Days Ago" / "N Day Ago" (case-insensitive): relative to now (UTC).
        - ISO-like date strings (e.g. 2026-03-10, 2026-03-10T12:00:00Z): parsed and returned as UTC.

    Returns:
        Timezone-aware datetime in UTC.

    Raises:
        ValueError: If value is empty or does not match the expected formats.
    """
    if not value or not value.strip():
        raise ValueError(
            'last_run must be a non-empty string: either "N Days Ago" (e.g. "7 Days Ago") '
            'or an ISO date/time (e.g. 2026-03-10 or 2026-03-10T12:00:00Z).'
        )
    raw = value.strip()
    m = _DAYS_AGO_RE.match(raw)
    if m:
        n = int(m.group(1))
        return datetime.now(timezone.utc) - timedelta(days=n)
    # Treat as ISO-like
    iso = raw.rstrip('Zz').rstrip()
    if raw.upper().endswith('Z'):
        iso += '+00:00'
    try:
        dt = datetime.fromisoformat(iso)
    except ValueError as e:
        raise ValueError(
            'last_run must be "N Days Ago" (e.g. "7 Days Ago") or an ISO date/time '
            '(e.g. 2026-03-10 or 2026-03-10T12:00:00Z).'
        ) from e
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def extract_pulse_ids(pulses_json: dict) -> List[str]:
    """Return a list of pulse IDs from an OTX response payload."""
    results = pulses_json.get('results', []) or []
    pulse_ids: List[str] = []
    for item in results:
        if 'id' in item:
            pulse_ids.append(str(item['id']))
    return pulse_ids


def extract_next_token(pulses_json: dict) -> Optional[str]:
    """Return the next page token (URL) from an OTX response payload."""
    next_token = pulses_json.get('next')
    return str(next_token) if next_token is not None else None


# Canonical targeted country names (semicolon-separated); used to normalize and dedupe.
_TARGETED_COUNTRIES_CANONICAL = (
    "Afghanistan;Albania;Algeria;American Samoa;Andorra;Angola;Antigua and Barbuda;Argentina;"
    "Armenia;Australia;Austria;Azerbaijan;Bahamas;Bahrain;Bangladesh;Barbados;Belarus;Belgium;"
    "Belize;Benin;Bermuda;Bhutan;Bolivia;Bosnia and Herzegovina;Botswana;Brazil;"
    "British Virgin Islands;Brunei;Brunei Darussalam;Bulgaria;Burkina Faso;Burundi;Cabo Verde;"
    "Cambodia;Cameroon;Canada;Cayman Islands;Central African Republic;Chad;Channel Islands;"
    "Chile;China;Colombia;Comoros;Congo (Brazzaville);Congo (Kinshasa);Costa Rica;Côte d'Ivoire;"
    "Croatia;Cuba;Cyprus;Czech Republic;Czechia;Denmark;Denmark (incl. Greenland);Djibouti;"
    "Dominica;Dominican Republic;Ecuador;Egypt;El Salvador;Equatorial Guinea;Eritrea;Estonia;"
    "Ethiopia;Federated States of Micronesia;Fiji;Finland;France;Gabon;Gambia;Georgia;Germany;"
    "Ghana;Gibraltar;Greece;Grenada;Guam;Guatemala;Guinea (Conakry);Guinea-Bissau;Guyana;Haiti;"
    "Honduras;Hong Kong;Hungary;Iceland;India;Indonesia;Iran;Iraq;Ireland;Isle of Man;Israel;"
    "Italy (incl. San Marino, Vatican State);Ivory Coast;Jamaica;Japan;Jordan;Kazakhstan;Kenya;"
    "Kiribati;Korea;Kosovo;Kuwait;Kyrgyzstan;Laos;Latvia;Lebanon;Lesotho;Liberia;Libya;"
    "Liechtenstein;Lithuania;Luxembourg;Macao;Madagascar;Malawi;Malaysia;Maldives;Mali;Malta;"
    "Marshall Islands;Mauritania;Mauritius;Mexico;Micronesia;Moldova;Monaco;Mongolia;"
    "Mongolia (part of China);Montenegro;Morocco;Mozambique;Myanmar (formerly Burma);Namibia;"
    "NATO;Nauru;Nepal;New Zealand;Nicaragua;Niger;Nigeria;North Korea;North Macedonia;"
    "Northern Ireland;Northern Mariana Islands;Norway;Oman;Pakistan;Palau;Palestine State;"
    "Palestinian Ruled Territories;Panama;Papua New Guinea;Paraguay;Peru;Philippines;Poland;"
    "Portugal;Qatar;Romania;Russian Federation;Rwanda;Saint Kitts and Nevis;Saint Lucia;"
    "Saint Vincent and the Grenadines;San Marino;Sao Tome and Principe;Saudi Arabia;Senegal;"
    "Serbia;Seychelles;Sierra Leone;Singapore;Slovakia;Slovenia;Solomon Islands;Somalia;"
    "South Africa;South Korea;South Sudan;Spain;Sri Lanka;Sudan;Suriname;Swaziland;Sweden;"
    "Switzerland;Syria;Taiwan;Tajikistan;Tanzania;Thailand;The Netherlands;Timor-Leste;Togo;"
    "Tonga;Trinidad & Tobago;Tunisia;Turkey;Turkmenistan;Turks and Caicos;Tuvalu;Uganda;Ukraine;"
    "UN;United Arab Emirates;United Kingdom;United States (US);Uruguay;US Virgin Islands;"
    "Uzbekistan;Vanuatu;Venezuela;Vietnam;Yemen;Zambia;Zimbabwe;Unknown"
)
_TARGETED_COUNTRIES_LOOKUP: dict[str, str] = {}
for _c in _TARGETED_COUNTRIES_CANONICAL.split(";"):
    _s = _c.strip()
    if _s:
        _TARGETED_COUNTRIES_LOOKUP[_s.lower()] = _s


def normalize_targeted_countries(value: Union[List[str], str]) -> List[str]:
    """Normalize targeted country names: strip, accept list or semicolon-separated string, map to canonical, dedupe."""
    if isinstance(value, str):
        tokens = [t.strip() for t in value.split(";") if t.strip()]
    else:
        tokens = [str(t).strip() for t in (value or []) if str(t).strip()]
    result: List[str] = []
    seen: set[str] = set()
    for t in tokens:
        key = t.lower()
        canonical = _TARGETED_COUNTRIES_LOOKUP.get(key, t)
        if key not in seen:
            seen.add(key)
            result.append(canonical)
    return result


def list_to_html_list(header: str,rows: List[str]) -> str:
    return f"<b>{header}</b><ul>{''.join(f'<li>{row}</li>' for row in rows)}</ul>"

def list_to_html_table(
    header: Union[str, List[str]],
    rows: Union[List[str], List[List[str]]],
) -> str:
    """Build an HTML table. If header is a list, table has multiple columns; rows must be list of row lists."""
    if isinstance(header, list):
        header_html = "".join(f"<th>{h}</th>" for h in header)
        header_html = f"<tr>{header_html}</tr>"
        rows_html = "".join(
            "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
            for row in rows
        )
    else:
        header_html = f"<tr><th>{header}</th></tr>"
        rows_html = "".join(f"<tr><td>{row}</td></tr>" for row in rows)
    return f"<table>{header_html}{rows_html}</table>"

def indicator_type_mapping(indicator_type: str) -> str:
    return {
        'domain': 'Host',
        'hostname': 'Host',
        'filehash-md5': 'File',
        'filehash-sha1': 'File',
        'filehash-sha256': 'File',
        'ipv4': 'Address',
        'ipv6': 'Address',
        'url': 'URL',
        'email': 'EmailAddress',
    }.get(indicator_type.lower(), indicator_type)



class App(PlaybookApp):
    """ThreatConnect Exchange App"""

    def __init__(self, _tcex: TcEx):
        """Initialize class properties."""
        super().__init__(_tcex)

        # properties
        self.batch = self.tcex.api.tc.v2.batch(self.in_.owner)

    def setup(self):
        """Perform prep/setup logic."""
        # setting the base url allow for subsequent API call
        # to be made by only providing the API endpoint/path.
        self.tcex.session.external.base_url = 'https://otx.alienvault.com/api/v1'
        self.tcex.session.external.headers.update(
            {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-OTX-API-KEY': self.in_.otx_api_key,
            }
        )

    def _fetch_pulses_page(self, session, url: str, params: Optional[dict] = None) -> Optional[dict]:
        """Fetch a single pulses page and return the parsed JSON payload."""
        r = session.get(url, params=params)
        if not r.ok:
            self.tcex.log.error(f'Response Code: {r.status_code}\nResponse Text: {r.text}')
            self.tcex.exit.exit(ExitCode.FAILURE, 'Failed to download data.')
            return None

        try:
            payload = r.json()
        except Exception:  # pragma: no cover - defensive programming
            self.tcex.log.error(f'Failed to parse response JSON: {r.text}')
            self.tcex.exit.exit(ExitCode.FAILURE, 'Failed to parse response JSON.')
            return None

        return payload

    def _fetch_pulse_detail(self, session, pulse_id: str) -> Optional[dict]:
        """Fetch details for a single pulse ID."""
        url = f'/pulses/{pulse_id}'
        r = session.get(url)
        if not r.ok:
            self.tcex.log.error(f'Response Code: {r.status_code}\nResponse Text: {r.text}')
            self.tcex.exit.exit(ExitCode.FAILURE, f'Failed to download details for pulse {pulse_id}.')
            return None

        try:
            payload = r.json()
        except Exception:  # pragma: no cover - defensive programming
            self.tcex.log.error(f'Failed to parse response JSON: {r.text}')
            self.tcex.log.error(f'Failed to parse details JSON for pulse {pulse_id}.')
            return None

        return payload

    def _extract_pulse_detail_fields(self, detail: dict) -> dict:
        """Extract fields from a pulse detail payload.

        This helper pulls values into individual variables so they can be
        easily adjusted or remapped later.
        """
        # Core metadata
        pulse_id = detail.get('id')
        name = detail.get('name')
        description = detail.get('description')
        author_name = detail.get('author_name')
        modified = detail.get('modified')
        created = detail.get('created')
        tlp = detail.get('TLP')
        adversary = {'name':detail.get('adversary'), 'type': 'Adversary'}

        if not name:
            self.tcex.exit.exit(ExitCode.FAILURE, f'JSON: {json.dumps(detail, indent=4)}')

        # High-level lists
        tags = detail.get('tags', [])
        references = detail.get('references', [])
        attack_ids = detail.get('attack_ids', [])
        targeted_countries = normalize_targeted_countries(detail.get('targeted_countries', []))
        malware_families = detail.get('malware_families', [])
        industries = detail.get('industries', [])

        # Author object
        author = detail.get('author') or {}
        author_username = author.get('username')
        author_id = author.get('id')
        author_avatar_url = author.get('avatar_url')

        # Raw indicators
        indicators = detail.get('indicators', [])

        # Derived indicator groupings
        associated_indicators = []
        for indicator in indicators:
            associated_indicators.append({
                'type': indicator_type_mapping(indicator.get('type')),
                'summary': indicator.get('indicator'),
            })

        all_tags = []
        if tags:
            all_tags.extend(tags)
        if attack_ids:
            all_tags.extend(attack_ids)
        if targeted_countries:
            all_tags.extend(targeted_countries)
        if malware_families:
            all_tags.extend(malware_families)
        if industries:
            all_tags.extend(naics_tags_for_keyword(industries))

        external_details = list_to_html_list("Author",[author_id, author_username, author_avatar_url])

        attributes = [
            {"type": "Description", "value": description, "displayed": True},
            {"type": "Author or Developer", "value": author_name},
            {"type": "External Date Last Modified", "value": modified},
            {"type": "External Date Created", "value": created},
            {"type": "External Reference", "value": list_to_html_table("Reference", references)},
            {"type": "External Details", "value": external_details},
            {"type": "External ID", "value": pulse_id},
        ]
        for country in targeted_countries:
            attributes.append({"type": "GeoCountry Targeted", "value": country})

        group = {
            'name': name,
            'description': description,
            'tags': all_tags,
            'attributes': attributes,
            'associated_groups': [adversary],
            'associated_indicators': associated_indicators,
            'type': 'Report',
        }

        if tlp:
            group['Security Label'] = f"TLP: {tlp.upper()}"

        return group

    # def _normalize_group_batch(self, group: dict) -> dict:
    #     """Normalize a group for batch creation."""
    #     xid = self.batch.generate_xid([self.in_.owner, group['type'], group['name']])
    #     # xid = self._generate_xid(group)
    #     group['xid'] = xid
    #     group_batch = {
    #             'name': group['name']
    #             , 'type': group['type']
    #             , 'xid': xid
    #         }

    #     if group.get('attributes', None):
    #         group_batch['attribute'] = group['attributes']

    #     if group.get('tags', None):
    #         group_batch['tag'] = group['tags']

    #     if group.get('associatedGroupXid', None):
    #         group_batch['associatedGroupXid'] = group['associatedGroupXid']

    #     return group_batch

    # def _normalize_indicator_batch(self, indicator: dict) -> dict:
    #     """Normalize an indicator for batch creation."""
    #     indicator_batch = self.batch.indicator(indicator['type'], indicator['summary'])
    #     associated_groups = indicator.get('associatedGroups', [])
    #     for xid in associated_groups:
    #         indicator_batch.association(xid)
    #     self.batch.save(indicator_batch)
        # return indicator_batch
        # self.batch.save(indicator_batch)
        # indicator_batch = {
        #     'type': indicator['type'],
        #     'summary': indicator['summary'],
        #     'xid': self.batch.generate_xid([self.in_.owner, indicator['type'], indicator['summary']])
        #     # 'xid': self._generate_xid(indicator)
        # }

        # if indicator.get('associatedGroups', None):
        #     indicator_batch['associatedGroupXid'] = indicator['associatedGroups']

        # return indicator_batch

    def _batch_create_groups(self, groups: List[dict]):
        """Batch create groups."""
        for group in groups:
            group_batch = self.batch.group(
                group['type']
                , group['name']
                , xid = self.batch.generate_xid([self.in_.owner, group['type'], group['name']])
            )

            attributes = group.get('attributes', [])
            for attribute in attributes:
                group_batch.attribute(attribute['type'], attribute['value'])
            
            tags = group.get('tags', [])
            # if tags:
            #     group_batch.tag(','.join(tags))
            for tag in tags:
                group_batch.tag(tag)

            if group.get('associatedGroupXid', None):
                group_batch.association(group['associatedGroupXid'])

            if group.get('Security Label', None):
                group_batch.security_label(group['Security Label'])

            self.batch.save(group_batch)

    def _batch_create_indicators(self, indicators: List[dict]):
        """Batch create indicators."""
        for indicator in indicators:
            indicator_batch = self.batch.indicator(indicator['type'], indicator['summary'])
            associated_group_xid = indicator.get('associatedGroupXid', None)
            if associated_group_xid:
                indicator_batch.association(associated_group_xid)
            self.batch.save(indicator_batch)

    def run(self):
        """Run main App logic."""
        last_run_raw = (self.in_.last_run or '').strip()
        try:
            last_run_dt = parse_last_run(last_run_raw)
        except ValueError as e:
            self.tcex.exit.exit(ExitCode.FAILURE, str(e))
            return
        modified_since_iso = last_run_dt.isoformat().replace('+00:00', 'Z')

        next_url: Optional[str] = '/pulses/subscribed'
        params: Optional[dict] = {'page': 1, 'modified_since': modified_since_iso}

        all_errors: List[dict] = []
        all_successes: List[dict] = []

        with self.tcex.session.external as s:
            first_page = True
            while next_url:
                # If next_url is absolute, rely on it entirely; otherwise treat as relative path.
                if next_url.startswith('http'):
                    url = next_url
                    page_params = None
                else:
                    url = next_url
                    page_params = params

                payload = self._fetch_pulses_page(s, url, page_params)
                if payload is None:
                    return

                page_pulse_ids = extract_pulse_ids(payload)

                if not page_pulse_ids:
                    self.tcex.log.info('No pulses found on current page.')
                else:
                    self.tcex.log.info(f'Processing {len(page_pulse_ids)} pulses on current page.')

                if first_page:
                    self.tcex.log.info('Data downloaded successfully.')
                    first_page = False

                next_url = extract_next_token(payload)
                if next_url:
                    self.tcex.log.info(f'Next page token: {next_url}')

                # After the first request, rely on the next URL for pagination.
                params = None

                # For this page, fetch pulse details and build groups/indicators.
                page_pulse_details: List[dict] = []
                for pulse_id in page_pulse_ids:
                    detail = self._fetch_pulse_detail(s, pulse_id)
                    if detail is not None:
                        fields = self._extract_pulse_detail_fields(detail)
                        page_pulse_details.append(fields)

                for group in page_pulse_details:
                    self._batch_create_groups([group])

                    associated_groups = group.get('associated_groups', [])
                    associated_indicators = group.get('associated_indicators', [])
                    group_xid = self.batch.generate_xid([self.in_.owner, group['type'], group['name']])

                    for associated_group in associated_groups:
                        associated_group['associatedGroupXid'] = group_xid
                    self._batch_create_groups(associated_groups)

                    for indicator in associated_indicators:
                        indicator['associatedGroupXid'] = group_xid
                    self._batch_create_indicators(associated_indicators)

                if page_pulse_details:
                    self.tcex.log.info(f'Submitting batch for {len(page_pulse_details)} pulses on current page.')
                    batch_response = self.batch.submit_all()

                    for item in batch_response:
                        all_errors.extend(item.get('errors', []))
                        all_successes.extend(item.get('successes', []))

        self.batch.close()

        if all_errors:
            self.tcex.log.error('App.run: batch submission failed with %d errors', len(all_errors))
            self.tcex.log.error('App.run: batch submission error: %s', all_errors[0])

        if all_successes:
            self.tcex.log.info('App.run: batch submission successful with %d items', len(all_successes))
            self.tcex.log.info('App.run: batch submission success: %s', all_successes[0])

        last_run_dt = datetime.now(timezone.utc)
        self.tcex.app.results_tc('last_run', last_run_dt.isoformat())
        self.tcex.log.info(f'Last run: {last_run_dt.isoformat()}')
        self.tcex.exit.exit(ExitCode.SUCCESS, f'Batch submission successful with {len(all_successes)} items.')

    def write_output(self):
        """Write the Playbook output variables.

        This method should be overridden with the output variables defined in the install.json
        configuration file.
        """
