import os
import argparse
import pathlib

import edgar


def cmd(args: argparse.Namespace):
    # create folder if not exists
    path = pathlib.Path(args.output).resolve().as_posix()
    if not os.path.exists(path):
        os.makedirs(path)

    if args.since_year < 1994:
        args.since_year = 1994

    # download index files using `python-edgar`
    edgar.download_index(
        path, args.since_year, args.user_agent, skip_all_present_except_last=True
    )
