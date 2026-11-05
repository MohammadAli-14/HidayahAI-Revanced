"""
Hidayah AI — Structured Logging
Provides a consistent logger for all modules, replacing raw print() calls.
"""

import logging
import sys

# Ensure UTF-8 console output on Windows to avoid UnicodeEncodeError with Arabic text
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

_LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s — %(message)s"
_DATE_FORMAT = "%H:%M:%S"


def _configure_root():
    """Configure the root Hidayah logger once."""
    root = logging.getLogger("hidayah")
    if root.handlers:
        return root
    root.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    root.addHandler(handler)
    return root


_configure_root()


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the 'hidayah' namespace.

    Usage:
        from utils.logger import get_logger
        log = get_logger(__name__)
        log.info("Something happened", extra={"surah": 2, "ayah": 255})
    """
    return logging.getLogger(f"hidayah.{name}")
