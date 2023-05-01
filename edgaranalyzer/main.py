import argparse
import pathlib
import sys
import os
import logging
from edgaranalyzer import __description__, __version__, CMD


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]...",
        description=__description__,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{parser.prog} version {__version__}",
    )
    parser.add_argument(
        "-l",
        "--log",
        metavar="log_path",
        help="set log file path",
        # default=f"{parser.prog}.log",
        default=None,
    )
    # subparsers
    subparsers = parser.add_subparsers(
        title="Sub-commands",
        dest="command",
        description="""Choose one from the following.
            Use `%(prog)s subcommand -h` to see help for each sub-command.""",
    )
    parser_download = subparsers.add_parser(
        CMD.DOWNLOAD_INDEX,
        description="""Download filings index files from EDGAR, 
            which contains the urls to actual filings""",
        help="Download filings index from EDGAR",
    )
    parser_download_filings = subparsers.add_parser(
        CMD.DOWNLOAD_FILINGS,
        description="""Download actual filings from EDGAR 
            (time-consuming!)""",
        help="Download filings from EDGAR",
    )
    parser_build_db = subparsers.add_parser(
        CMD.BUILD_DATABASE,
        description="Build database of filings",
        help="Build database",
    )
    # find & search
    parser_find_items = subparsers.add_parser(
        CMD.FIND_ITEMS,
        description="""Find reported items from filings
            from header data""",
        help="Find reported items from filings",
    )
    parser_find_event_date = subparsers.add_parser(
        CMD.FIND_EVENT_DATE,
        description="""Find event date from filings
            from header data""",
        help="Find event date from filings",
    )
    parser_find_zipcode = subparsers.add_parser(
        CMD.FIND_ZIPCODE,
        description="""Find business zipcode from filings
            from header data""",
        help="Find reported zipcode from filings",
    )
    parser_find_loans = subparsers.add_parser(
        CMD.FIND_LOANS,
        description="""Find loan contracts from filings
            using Nini, Smith and Sufi (2009 JFE)""",
        help="Find loan contracts from filings",
    )
    parser_find_loan_signature = subparsers.add_parser(
        CMD.FIND_LOAN_SIGNATURE,
        description="""Find loan contracts from filings
            with signature page""",
        help="Find loans with signature from filings",
    )
    parser_sample_loans = subparsers.add_parser(
        CMD.SAMPLE_LOANS,
        description="Randomly sample loan contracts from filings",
        help="Sample loan contracts from filings",
    )

    parser_build_db.add_argument(
        "-db",
        "--database",
        metavar="database",
        default="edgar-idx.sqlite3",
        help="output sqlite database to store results. Defaults to `edgar-idx.sqlite3`",
    )
    required = parser_build_db.add_argument_group("required named arguments")
    required.add_argument(
        "-i",
        "--inputdir",
        metavar="inputdir",
        help="input directory of index files from `download_index`",
    )

    parser_download_filings.add_argument(
        "-t",
        "--threads",
        metavar="threads",
        help="number of processes to use",
        default=4,
    )
    required = parser_download_filings.add_argument_group("required named arguments")
    required.add_argument(
        "-ua",
        "--user_agent",
        required=True,
        metavar="user_agent",
        help="""User-Agent in request's headers 
            (e.g., "MyCompany bob@mycompany.com")""",
    )
    required.add_argument(
        "--file_type",
        required=True,
        metavar="file_type",
        help="type of filing",
    )
    required.add_argument(
        "-o",
        "--output",
        required=True,
        metavar="output",
        help="output directory",
    )
    required.add_argument(
        "-db",
        "--database",
        metavar="databsae",
        help="sqlite database to store results",
    )

    # subparser for `download_index` subcommand
    required = parser_download.add_argument_group("required named arguments")
    required.add_argument(
        "-ua",
        "--user_agent",
        required=True,
        metavar="user_agent",
        help="""User-Agent in request's headers 
            (e.g., "MyCompany bob@mycompany.com")""",
    )
    required.add_argument(
        "-o",
        "--output",
        required=True,
        metavar="output",
        help="output directory",
    )
    parser_download.add_argument(
        "-b",
        "--since_year",
        metavar="since_year",
        default="2022",
        type=int,
        help="since year (YYYY)",
    )

    for p in [
        parser_find_items,
        parser_find_loans,
        parser_find_zipcode,
        parser_find_event_date,
        parser_find_loan_signature,
        parser_sample_loans,
    ]:
        required = p.add_argument_group("required named arguments")
        required.add_argument(
            "-d",
            "--data_dir",
            required=True,
            metavar="data_directory",
            help="directory of filings",
        )
        required.add_argument(
            "--file_type",
            required=True,
            metavar="file_type",
            help="type of filing",
        )
        required.add_argument(
            "-db",
            "--database",
            metavar="databsae",
            help="sqlite database to store results",
        )

    for p in [
        parser_find_items,
        parser_find_loans,
        parser_find_zipcode,
        parser_find_event_date,
        parser_find_loan_signature,
    ]:
        p.add_argument(
            "-t",
            "--threads",
            metavar="threads",
            help="number of processes to use",
            default=os.cpu_count(),
        )

    parser_find_loans.add_argument(
        "--skip_init_table",
        default=False,
        const=True,
        action="store_const",
        help="if set, skip init table step",
    )

    parser_sample_loans.add_argument(
        "-n",
        default=10,
        type=int,
        help="number of loan filings to sample (default=10)",
    )
    parser_sample_loans.add_argument(
        "--out_dir",
        metavar="out_dir",
        default=os.getcwd(),
        help="output directory",
    )

    return parser


def main():
    parser = init_argparse()
    args = parser.parse_args()

    if args.log is None:
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format="%(levelname)s - %(asctime)s - %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p",
        )
    else:
        log_path = pathlib.Path(args.log).resolve().as_posix()
        logging.basicConfig(
            filename=log_path,
            level=logging.DEBUG,
            filemode="w",
            format="%(levelname)s - %(asctime)s - %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p",
        )

    match args.command:
        case CMD.BUILD_DATABASE:
            from .cmd_build_database import cmd
        case CMD.DOWNLOAD_INDEX:
            from .cmd_download_index import cmd
        case CMD.DOWNLOAD_FILINGS:
            from .cmd_download_filings import cmd
        case CMD.FIND_ITEMS:
            from .cmd_find_items import cmd
        case CMD.FIND_ZIPCODE:
            from .cmd_find_zipcode import cmd
        case CMD.FIND_LOANS:
            from .cmd_find_loans import cmd
        case CMD.FIND_EVENT_DATE:
            from .cmd_find_event_date import cmd
        case CMD.SAMPLE_LOANS:
            from .cmd_sample_loans import cmd
        case CMD.FIND_LOAN_SIGNATURE:
            from .cmd_find_loan_signature import cmd
        case _:
            cmd = lambda _: None

    cmd(args)


if __name__ == "__main__":
    main()
