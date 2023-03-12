import argparse
import logging
import os
import re
import tempfile
import types
import requests_html

from edgaranalyzer import CMD
from .cmd_find import cmd_find
from .utils import prefix_logger, walk_dirpath, extract_files


logger = prefix_logger(CMD.FIND_LOANS, logging.getLogger(__name__))

sql = types.SimpleNamespace()
sql.create_table = """CREATE TABLE IF NOT EXISTS files_with_loan_contracts
    (cik TEXT, file_type TEXT, date DATE, has_loan INTEGER,
    PRIMARY KEY(cik, file_type, date));"""

sql.insert_result = """INSERT OR IGNORE INTO files_with_loan_contracts
    (cik, file_type, date, has_loan) VALUES (?,?,?,?);"""


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
        files = extract_files(filepath, tempfile.gettempdir())
        has_loan_in_one_or_more_docs = False
        for file in files:
            if has_loan(file):
                has_loan_in_one_or_more_docs = True
                break
        if has_loan_in_one_or_more_docs:
            matches.append((cik, date, file_type, "TRUE"))
        else:
            matches.append((cik, date, file_type, "FALSE"))

    return matches


# Regex pattern used to find the appearance of any of the 10 search words used
# in "Creditor control rights and firm investment policy"
# by Nini, Smith and Sufi (JFE 2009)
# pat_10_words = r"CREDIT FACILITY|REVOLVING CREDIT|(CREDIT|LOAN|(LOAN (AND|&) \
#    SECURITY)|(FINANCING (AND|&) SECURITY)|CREDIT (AND|&) GUARANTEE) AGREEMENT"
NSS_10_words = [
    "credit facility",
    "revolving credit",
    "credit agreement",
    "loan agreement",
    "loan and security agreement",
    "loan & security agreement",
    "credit and guarantee agreement",
    "credit & guarantee agreement",
    "financing and security agreement",
    "financing & security agreement",
]
NSS_10_words_str = "|".join([word.upper() for word in NSS_10_words])
pat_10_words = re.compile(NSS_10_words_str)


def has_loan(path: str) -> bool:
    with open(path, "r") as f:
        text = f.read()
    html = requests_html.HTML(html=text)
    match = pat_10_words.search(html.text)
    return True if match else False
