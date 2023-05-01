import argparse
import os
import pathlib
import sqlite3

EDGAR_BASE = "https://www.sec.gov/Archives/"


def cmd(args: argparse.Namespace):
    inputdir = pathlib.Path(args.inputdir).resolve().as_posix()

    assert os.path.exists(inputdir)

    dbpath = pathlib.Path(args.database).resolve().as_posix()
    if not os.path.exists(os.path.dirname(dbpath)):
        os.makedirs(os.path.dirname(dbpath))

    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS edgar_idx 
        (cik TEXT, firm_name TEXT, file_type TEXT, date DATE, url TEXT);"""
    )

    for dirpath, _, filenames in os.walk(inputdir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            print(f"Populating database using {filepath}")
            with open(filepath, "r") as f:
                lines = f.readlines()
            data = [parse(line) for line in lines]
            c.executemany(
                "INSERT OR IGNORE INTO edgar_idx \
                    (cik, firm_name, file_type, date, url) VALUES (?,?,?,?,?)",
                data,
            )

    conn.commit()
    conn.close()


def parse(line):
    # each line: "cik|firm_name|file_type|date|url_txt|url_html"
    # an example:
    # "99780|TRINITY INDUSTRIES INC|8-K|2020-01-15|edgar/data/99780/0000099780-\
    # 20-000008.txt|edgar/data/99780/0000099780-20-000008-index.html"
    line = tuple(line.split("|")[:5])
    l = list(line)
    l[-1] = EDGAR_BASE + l[-1]
    return tuple(l)
