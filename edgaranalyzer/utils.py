import logging
import pathlib
import os
import gzip
from typing import Mapping, List


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


def extract_files(file_path: str, out_dir: str) -> List[str]:
    """Extract docs in a gzipped filing into the out directory

    Args:
        file_path (str): path to the gzipped filing
        out_dir (str): output directory path

    Returns:
        List[str]: list of the extracted document paths
    """
    path = pathlib.Path(file_path).expanduser().resolve().as_posix()
    outpath = pathlib.Path(out_dir).expanduser().resolve().as_posix()
    if ".gz" not in path:
        return []
    f = gzip.open(file_path, "rt")
    # logger.info(f"extracting files from {file_path}")
    # Find number of documents in this filing
    while not (line := f.readline()).startswith("PUBLIC DOCUMENT COUNT"):
        if not line:
            break
    n_docs = int(line.replace(" ", "").split(":")[-1]) if line else 1
    # logger.info(f"{n_docs} documents from {file_path}")
    # Split into documents
    _, file_type = os.path.split(os.path.dirname(path))
    _, cik = os.path.split(os.path.dirname(os.path.dirname(path)))
    docs = []
    for ith_doc in range(1, n_docs + 1):
        doc_started = False
        ith_doc_file_name = os.path.split(file_path)[-1].replace(
            ".txt.gz", f".doc-{ith_doc}.txt"
        )
        ith_doc_file_name = f"{cik}.{file_type}.{ith_doc_file_name}"
        # split into documents
        ith_doc_file = os.path.join(outpath, ith_doc_file_name)
        with open(ith_doc_file, "w") as ftmp:
            while line := f.readline():
                if line.startswith("<DOCUMENT>"):
                    doc_started = True
                if line.startswith("<FILENAME>"):
                    doc_name = line.strip("<FILENAME>").strip().lower()
                if doc_started:
                    ftmp.write(line)
                if line.startswith("</DOCUMENT>"):
                    doc_started = False
                    break
        if os.path.getsize(ith_doc_file) == 0:
            os.remove(ith_doc_file)
            continue
        # rename splited documents based on its name in the filing
        if doc_name.endswith("htm") or doc_name.endswith("html"):
            newname = ith_doc_file.replace("txt", doc_name)
            os.rename(ith_doc_file, newname)
            # logger.debug(f"document {ith_doc}: {newname}")
            docs.append(newname)
        elif doc_name.endswith("txt"):
            # logger.debug(f"document {ith_doc}: {doc_name}")
            docs.append(ith_doc_file)
        else:
            # JPG, PNG, XML, etc., other types of filings
            # logger.debug(f"document {ith_doc} skipped (jpg, png, xml, etc.)")
            os.remove(ith_doc_file)
    f.close()
    return docs
