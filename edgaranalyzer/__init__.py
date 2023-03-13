import types

__version__ = "0.0.1"
__description__ = "Textual analysis on SEC filings from EDGAR"
__author__ = "Mingze Gao"
__author_email__ = "mingze.gao@sydney.edu.au"
__url__ = "https://github.com/mgao6767/edgar-analyzer"

CMD = types.SimpleNamespace()
CMD.DOWNLOAD_INDEX = "download_index"
CMD.DOWNLOAD_FILINGS = "download_filings"
CMD.BUILD_DATABASE = "build_database"
CMD.FIND_ITEMS = "find_reported_items"
CMD.FIND_LOANS = "find_loan_contracts"
CMD.FIND_LOAN_SIGNATURE = "find_loan_signature"
CMD.SAMPLE_LOANS = "sample_loan_contracts"
