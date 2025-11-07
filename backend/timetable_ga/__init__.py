# timetable_ga/__init__.py
"""
timetable_ga: Genetic Algorithm for weekly timetable scheduling.

Public API:
- run_ga: main GA entrypoint
- GAInput, Gene, Subject, Section, Room, Faculty: core dataclasses
- chromosome_to_rows: encode GA result to API/DB rows
"""

from .ga import run_ga
from .models import (
    GAInput,
    Gene,
    Subject,
    Section,
    Room,
    Faculty,
)
from .encoder import chromosome_to_rows

__all__ = [
    "run_ga",
    "GAInput",
    "Gene",
    "Subject",
    "Section",
    "Room",
    "Faculty",
    "chromosome_to_rows",
]

__version__ = "0.1.0"

# Optional: very light logger helper (no heavy config here)
import logging

def get_logger(name: str = "timetable_ga") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Keep it minimal; app.py can configure root logging.
        handler = logging.StreamHandler()
        fmt = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger