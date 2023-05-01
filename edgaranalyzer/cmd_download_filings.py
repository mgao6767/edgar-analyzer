import argparse
import pathlib
import os
import sqlite3
import random
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import tqdm
import pandas as pd


LAST_REQ_TIME = 0
QUERY_FILINGS = """SELECT CIK, FILE_TYPE, DATE, URL FROM EDGAR_IDX;"""


def download(job, progress):
    global LAST_REQ_TIME
    headers, datadir, cik, file_type, date, url = job
    if round(time.time() * 1000) - LAST_REQ_TIME < 100:
        time.sleep(0.1)

    filename = os.path.join(datadir, cik, file_type, f"{date}.txt.gz")
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    req = urllib.request.Request(url, headers=headers)
    res = urllib.request.urlopen(req)
    LAST_REQ_TIME = round(time.time() * 1000)
    if res.status != 200:
        return 1
    with open(filename, "wb") as f:
        f.write(res.read())
        progress.update()
    return 0


def cmd(args: argparse.Namespace):
    dbpath = pathlib.Path(args.database).resolve().as_posix()
    assert os.path.exists(dbpath)

    datadir = pathlib.Path(args.output).resolve().as_posix()
    if not os.path.exists(datadir):
        os.makedirs(datadir)

    headers = {
        "User-Agent": args.user_agent,
        "Accept-Encoding": "gzip, deflate",
        "Host": "www.sec.gov",
    }

    # Find out the missing ones on the disk
    conn = sqlite3.connect(dbpath)
    df = pd.read_sql_query(QUERY_FILINGS, conn)
    conn.close()

    df = df[df["file_type"] == args.file_type]

    jobs = []
    for _, (cik, file_type, date, url) in df.iterrows():
        datapath = os.path.join(datadir, cik, file_type, f"{date}.txt.gz")
        if not os.path.exists(datapath):
            jobs.append((headers, datadir, cik, file_type, date, url))

    # Download only the missing filings on the disk
    progress = tqdm.tqdm(total=len(jobs))
    random.shuffle(jobs)
    with ThreadPoolExecutor(max_workers=int(args.threads)) as exe:
        fs = []
        for job in jobs:
            fs.append(exe.submit(download, job, progress))

        for _ in as_completed(fs):
            pass
