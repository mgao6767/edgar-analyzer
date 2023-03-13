import argparse
import logging
import os
import pathlib
import sqlite3

from edgaranalyzer import CMD
from .utils import prefix_logger, extract_files


logger = prefix_logger(CMD.FIND_LOANS, logging.getLogger(__name__))


def cmd(args: argparse.Namespace):
    path = pathlib.Path(args.data_dir).expanduser().resolve().as_posix()
    db = pathlib.Path(args.database).expanduser().resolve().as_posix()
    out = pathlib.Path(args.out_dir).expanduser().resolve().as_posix()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(
        f"""SELECT * FROM files_with_loan_contracts 
        WHERE file_type="{args.file_type}" AND has_loan="TRUE"
        ORDER BY RANDOM() LIMIT {args.n};"""
    )
    result = c.fetchall()
    conn.close()

    paths = [
        os.path.join(path, cik, file_type, f"{date}.txt.gz")
        for cik, file_type, date, _ in result
    ]
    for p in paths:
        extract_files(p, out)
