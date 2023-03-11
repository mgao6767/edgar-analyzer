import logging
import pathlib
import os
from typing import Mapping


class prefix_logger(logging.LoggerAdapter):
    """Prefix a logger message"""

    def __init__(
        self, prefix, logger, extra: Mapping[str, object] | None = None
    ) -> None:
        super().__init__(logger, extra)
        self.prefix = prefix

    def process(self, msg, kwargs):
        return f"[{self.prefix}] - {msg}", kwargs


def walk_dirpath(dir_path: str, cik: str, file_type: str) -> str:
    """Yield filing paths in the given directory

    Args:
        dir_path (str): data directory of all filings
        cik (str): cik of company
        file_type (str): filing type, e.g., "8-K", "10-K"

    Yields:
        str: filing path
    """
    path = pathlib.Path(dir_path).joinpath(cik, file_type)
    path = path.expanduser().resolve()

    for dirpath, _, filenames in os.walk(path):
        for filename in [f for f in filenames if f.endswith(".txt.gz")]:
            yield os.path.join(dirpath, filename)
