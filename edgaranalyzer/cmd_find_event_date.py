import argparse
import logging
import os
import gzip
import types
from datetime import datetime

from edgaranalyzer import CMD
from .cmd_find import cmd_find
from .utils import prefix_logger, walk_dirpath


logger = prefix_logger(CMD.FIND_EVENT_DATE, logging.getLogger(__name__))

sql = types.SimpleNamespace()
sql.create_table = """CREATE TABLE IF NOT EXISTS files_event_date
    (cik TEXT, file_type TEXT, date DATE, event_date DATE,
    PRIMARY KEY(cik, file_type, date));"""

sql.insert_result = """INSERT OR IGNORE INTO files_event_date
    (cik, file_type, date, event_date) VALUES (?,?,?,?);"""


def cmd(args: argparse.Namespace):
    cmd_find(args, logger, sql, regsearch)


def regsearch(path: str, cik: str, file_type: str) -> list:
    """Search function on a filing

    Args:
        path (str): data directory
        cik (str): cik of company
        file_type (str): file type, e.g., "8-K", "10-K"

    Returns:
        list: list of results
    """
    matches = []
    for filepath in walk_dirpath(path, cik, file_type):
        date = os.path.split(filepath)[-1].strip(".txt.gz")
        with gzip.open(filepath, "rt") as f:
            while (
                not (line := f.readline())
                .strip()
                .startswith("CONFORMED PERIOD OF REPORT")
            ):
                if not line:
                    break

            event_date = line.split(":")[-1].strip()

            event_date = event_date.strip() if isinstance(event_date, str) else ""
            if len(event_date):
                event_date = datetime.strptime(event_date, "%Y%m%d").strftime(
                    "%Y-%m-%d"
                )

            matches.append((cik, file_type, date, event_date))

    return matches
