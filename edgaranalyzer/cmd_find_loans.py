import argparse
import logging
import os
import re
import pathlib
import sqlite3
import types
import tqdm
import requests_html
import sys

from edgaranalyzer import CMD
from .cmd_find import cmd_find
from .utils import prefix_logger, walk_dirpath, extract_files

# Increase recursion limit for parsing large HTML
sys.setrecursionlimit(1_000_000_000)

logger = prefix_logger(CMD.FIND_LOANS, logging.getLogger(__name__))

sql = types.SimpleNamespace()
sql.create_table = """CREATE TABLE IF NOT EXISTS files_with_loan_contracts
    (cik TEXT, file_type TEXT, date DATE, has_loan INTEGER,
    PRIMARY KEY(cik, file_type, date));"""

sql.init = """INSERT OR IGNORE INTO files_with_loan_contracts
    (cik, file_type, date, has_loan) VALUES (?,?,?,?);"""

sql.insert_result = """INSERT OR REPLACE INTO files_with_loan_contracts
    (cik, file_type, date, has_loan) VALUES (?,?,?,?);"""

temp_dir = os.path.join(os.path.dirname(__file__), "__temp")


def cmd(args: argparse.Namespace):
    if not args.skip_init_table:
        create_table_in_db(args)
    os.makedirs(temp_dir, exist_ok=True)
    skip_ciks = checked_ciks(args)
    cmd_find(args, logger, sql, regsearch, skip_ciks)
    if os.path.exists(temp_dir):
        os.removedirs(temp_dir)


def create_table_in_db(args: argparse.Namespace):
    path = pathlib.Path(args.data_dir).expanduser().resolve().as_posix()
    db = pathlib.Path(args.database).expanduser().resolve().as_posix()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    logger.debug("create table in database, if not exists")
    c.execute(sql.create_table)
    _, ciks, _ = next(os.walk(path))
    logger.debug("init table in database")
    progress = tqdm.tqdm(total=len(ciks))
    for cik in ciks:
        values = []
        for filepath in walk_dirpath(path, cik, args.file_type):
            date = os.path.split(filepath)[-1].strip(".txt.gz")
            values.append((cik, args.file_type, date, None))
        c.executemany(sql.init, values)
        conn.commit()
        progress.update()
    conn.close()
    logger.debug("init table done")


def checked_ciks(args: argparse.Namespace):
    db = pathlib.Path(args.database).expanduser().resolve().as_posix()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(
        f"""SELECT DISTINCT cik FROM files_with_loan_contracts 
    WHERE has_loan IS NOT NULL AND file_type="{args.file_type}";"""
    )
    skip_ciks = [cik for (cik,) in c.fetchall()]
    conn.close()
    return skip_ciks


def regsearch(path: str, cik: str, file_type: str) -> list:
    """Search function on filings of a cik

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
        files = extract_files(filepath, temp_dir)
        has_loan_in_one_or_more_docs = False
        for file in files:
            if has_loan(file):
                has_loan_in_one_or_more_docs = True
                break
        if has_loan_in_one_or_more_docs:
            matches.append((cik, file_type, date, "TRUE"))
        else:
            matches.append((cik, file_type, date, "FALSE"))
        for file in files:
            os.remove(file)

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
