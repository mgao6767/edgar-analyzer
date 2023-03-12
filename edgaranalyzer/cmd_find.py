import argparse
import pathlib
import typing
import os, sys
import types
import sqlite3
import random
import concurrent.futures
import tqdm

from .utils import prefix_logger


def cmd_find(
    args: argparse.Namespace,
    logger: prefix_logger,
    sql: types.SimpleNamespace,
    regsearch: typing.Callable,
    skip_ciks: list = [],
):
    path = pathlib.Path(args.data_dir).expanduser().resolve().as_posix()
    db = pathlib.Path(args.database).expanduser().resolve().as_posix()

    logger.info("started")
    logger.info(f"data directory: {path}")
    if not os.path.exists(path):
        logger.error("data directory does not exist")
        sys.exit(1)

    logger.info(f"database: {db}")
    if not os.path.exists(db):
        logger.warning("database does not exist")
        logger.info("creating database")

    logger.debug("connecting database")
    conn = sqlite3.connect(db)
    c = conn.cursor()
    logger.debug("create table in database, if not exists")
    c.execute(sql.create_table)
    conn.commit()

    _, ciks, _ = next(os.walk(path))

    workers = min(os.cpu_count(), int(args.threads))
    file_type = args.file_type
    logger.info(f"total ciks: {len(ciks)}")
    logger.info(f"filing type: {file_type}")
    logger.info(f"workers: {workers}")

    logger.info("start processing")
    ciks = [cik for cik in ciks if cik not in skip_ciks]
    progress = tqdm.tqdm(total=len(ciks))
    random.shuffle(ciks)
    with concurrent.futures.ProcessPoolExecutor(workers) as exe:
        futures = [exe.submit(regsearch, path, cik, file_type) for cik in ciks]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res:
                c.executemany(sql.insert_result, res)
                conn.commit()
            progress.update()
    logger.info("finishe processing")

    conn.close()
    logger.debug("database closed")
    logger.info("finished")
