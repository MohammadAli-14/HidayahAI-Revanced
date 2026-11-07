import os
import xml.etree.ElementTree as ET
from pathlib import Path
import pytest
from utils.config import LOGO_PATH, get_logo_base64, _DEFAULT_LOGO_SVG


def test_logo_path_resolves_to_svg():
    """Verify that LOGO_PATH resolves to the master vector SVG."""
    assert LOGO_PATH.exists(), f"Logo file does not exist at {LOGO_PATH}"
    assert LOGO_PATH.name == "hidayah_logo.svg", f"Expected hidayah_logo.svg, got {LOGO_PATH.name}"


def test_logo_xml_validity():
    """Verify that the master SVG is valid, well-formed XML with expected dimensions."""
    tree = ET.parse(LOGO_PATH)
    root = tree.getroot()
    assert root.tag.endswith("svg"), f"Root tag must be SVG, got {root.tag}"
    assert root.attrib.get("viewBox") == "0 0 512 512", "Master emblem viewBox must be '0 0 512 512'"


def test_get_logo_base64():
    """Verify that get_logo_base64 returns a proper data URI."""
    uri = get_logo_base64()
    assert uri.startswith("data:image/svg+xml;base64,"), "URI must start with proper SVG mime type"
    assert len(uri) > 1000, "Base64 payload must be non-trivial"


def test_frontend_logo_suite_exists():
    """Verify that all production SVG variants exist in frontend/public/logos."""
    root_dir = Path(__file__).resolve().parent.parent
    logos_dir = root_dir / "frontend" / "public" / "logos"

    expected_files = [
        "hidayah_app_icon.svg",
        "hidayah_logo_transparent.svg",
        "hidayah_logo_horizontal.svg",
    ]

    for fname in expected_files:
        fpath = logos_dir / fname
        assert fpath.exists(), f"Missing production logo asset: {fpath}"
        # Validate XML
        tree = ET.parse(fpath)
        root = tree.getroot()
        assert root.tag.endswith("svg"), f"File {fname} is not valid SVG"
