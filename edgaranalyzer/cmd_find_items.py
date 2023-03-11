import argparse
import logging
import os
import gzip
import types

from edgaranalyzer import CMD
from .cmd_find import cmd_find
from .utils import prefix_logger, walk_dirpath


logger = prefix_logger(CMD.FIND_ITEMS, logging.getLogger(__name__))

sql = types.SimpleNamespace()
sql.create_table = """CREATE TABLE IF NOT EXISTS files_all_items
    (cik TEXT, file_type TEXT, date DATE, item TEXT,
    PRIMARY KEY(cik, file_type, date, item));"""

sql.insert_result = """INSERT OR IGNORE INTO files_all_items 
    (cik, file_type, date, item) VALUES (?,?,?,?);"""


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
        with gzip.open(filepath, "rb") as f:
            while not (line := f.readline()).startswith(b"ITEM INFORMATION"):
                if not line:
                    break
            while line.startswith(b"ITEM INFORMATION"):
                item = line.decode().split(":")[-1].strip()
                if len(item):
                    matches.append((cik, file_type, date, item.upper()))
                line = f.readline()
    return matches
