import argparse
import logging
import os
import gzip
import types

from edgaranalyzer import CMD
from .cmd_find import cmd_find
from .utils import prefix_logger, walk_dirpath


logger = prefix_logger(CMD.FIND_ZIPCODE, logging.getLogger(__name__))

sql = types.SimpleNamespace()
sql.create_table = """CREATE TABLE IF NOT EXISTS files_zipcode
    (cik TEXT, file_type TEXT, date DATE, state TEXT, zipcode TEXT,
    PRIMARY KEY(cik, file_type, date));"""

sql.insert_result = """INSERT OR IGNORE INTO files_zipcode
    (cik, file_type, date, state, zipcode) VALUES (?,?,?,?,?);"""


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
            while not (line := f.readline()).strip().startswith("BUSINESS ADDRESS"):
                if not line:
                    break

            while not line.strip().startswith("STATE"):
                line = f.readline()
                if not line:
                    break
            state = line.split(":")[-1]
            state = state.strip() if isinstance(state, str) else ""

            while not line.strip().startswith("ZIP"):
                line = f.readline()
                if not line:
                    break
            zip = line.split(":")[-1].strip()
            zip = zip.strip() if isinstance(zip, str) else ""

            matches.append((cik, file_type, date, state.upper(), zip.upper()))

    return matches
