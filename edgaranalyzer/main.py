import argparse

from edgaranalyzer import __description__, __version__


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
        "download_index",
        description="""Download filings index files from EDGAR, 
            which contains the urls to actual filings""",
        help="Download filings index from EDGAR",
    )
    parser_download_filings = subparsers.add_parser(
        "download_filings",
        description="""Download actual filings from EDGAR 
            (time-consuming!)""",
        help="Download filings from EDGAR",
    )

    parse_build_db = subparsers.add_parser(
        "build_database",
        description="Build database of filings",
        help="Build database",
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
        help="output file path",
    )
    parser_download.add_argument(
        "-b",
        "--since_year",
        metavar="since_year",
        default="2022",
        type=int,
        help="since year (YYYY)",
    )
    return parser


def main():
    parser = init_argparse()
    args = parser.parse_args()

    if args.command == "download_index":
        from .cmd_download_index import cmd_download_index

        cmd_download_index(args)

    if args.command == "download_filings":
        from .cmd_download_filings import cmd_download_filings

        cmd_download_filings(args)

    if args.command == "build_database":
        from .cmd_build_database import cmd_build_database

        cmd_build_database(args)


if __name__ == "__main__":
    main()
