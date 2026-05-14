"""Helpers for converting XML to JSON-serializable Python objects."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from xml.etree import ElementTree as ET


JsonValue = str | list['JsonValue'] | dict[str, 'JsonValue']


def _element_to_obj(elem: ET.Element) -> JsonValue:
    """Convert an XML element into a JSON-serializable Python object.

    Rules:
    - Tag names become keys.
    - Leaf nodes become their stripped text (or '' if empty).
    - Repeated child tags become lists in document order.
    - Attributes are ignored.
    - Mixed content parent text is ignored when child elements exist.
    """

    # If there are no child elements, return the element text.
    if len(list(elem)) == 0:
        return (elem.text or '').strip()

    result: dict[str, JsonValue] = {}
    for child in list(elem):
        key = child.tag
        value = _element_to_obj(child)

        existing = result.get(key)
        if existing is None:
            result[key] = value
        elif isinstance(existing, list):
            existing.append(value)
        else:
            result[key] = [existing, value]

    return result


def xml_to_json(xml_str: str) -> dict[str, JsonValue]:
    """Convert an XML string into a JSON object (Python dict).

    Args:
        xml_str: A string containing XML.

    Returns:
        A dict containing a single key (the root tag) mapped to a JSON-serializable
        Python value (dict/list/str).

    Raises:
        ValueError: If xml_str is empty/whitespace or cannot be parsed as XML.
    """

    if xml_str is None or not str(xml_str).strip():
        raise ValueError('XML input is empty.')

    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError as e:
        raise ValueError(f'Failed parsing XML data ({e}).') from e

    obj = _element_to_obj(root)
    if isinstance(obj, Mapping):
        return {root.tag: dict(obj)}
    return {root.tag: obj}
