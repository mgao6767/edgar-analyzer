import argparse
import types
from edgaranalyzer import __description__, __version__

CMD = types.SimpleNamespace()
CMD.DOWNLOAD_INDEX = "download_index"
CMD.DOWNLOAD_FILINGS = "download_filings"
CMD.BUILD_DATABASE = "build_database"
CMD.FIND_ITEMS = "find_reported_items"
CMD.FIND_LOANS = "find_loan_contracts"


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
    parser_find_loans = subparsers.add_parser(
        CMD.FIND_LOANS,
        description="""Find loan contracts from filings
            using Nini, Smith and Sufi (2009 JFE)""",
        help="Find loan contracts from filings",
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

    # subparser for `find_items` subcommand
    required = parser_find_items.add_argument_group("required named arguments")
    required.add_argument(
        "-d",
        "--data_dir",
        required=True,
        metavar="data_directory",
        help="directory of filings",
    )
    required.add_argument(
        "-db",
        "--database",
        metavar="databsae",
        help="sqlite database to store results",
    )

    # subparser for `find_filings` subcommand
    required = parser_find_loans.add_argument_group("required named arguments")
    required.add_argument(
        "-d",
        "--data_dir",
        required=True,
        metavar="data_directory",
        help="directory of filings",
    )
    required.add_argument(
        "-db",
        "--database",
        metavar="databsae",
        help="sqlite database to store results",
    )

    return parser


def main():
    parser = init_argparse()
    args = parser.parse_args()

    match args.command:
        case CMD.BUILD_DATABASE:
            from .cmd_build_database import cmd
        case CMD.DOWNLOAD_INDEX:
            from .cmd_download_index import cmd
        case CMD.DOWNLOAD_FILINGS:
            from .cmd_download_filings import cmd
        case CMD.FIND_ITEMS:
            from .cmd_find_items import cmd
        case CMD.FIND_LOANS:
            from .cmd_find_loans import cmd
        case _:
            cmd = lambda _: None

    cmd(args)


if __name__ == "__main__":
    main()
