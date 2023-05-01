# `edgar-analyzer` - Textual Analysis with EDGAR filings

`edgar-analyzer` is a CLI tool to download SEC filings from EDGAR and perform textual analyses.

## Installation

```bash
pip install edgar-analyzer
```

## Workflow

### Setup

**Download index files**, which contain the firm CIK, name, filing date, type, and URL of the filing.

```bash
edgar-analyzer download_index --user_agent "MyCompany name@mycompany.com" --output "./index"
```

**Build a database** of the previously download index files for more efficient queries.

```bash
edgar_analyzer build_database --inputdir "./index" --database "edgar-idx.sqlite3"
```

**Download filings**, only filings in the database but not downloaded yet will be downloaded. Download speed will be auto throttled as per SEC's fair use policy.

```bash
edgar-analyzer download_filings --user_agent "MyCompany name@mycompany.com" --output "./output" --database "edgar-idx.sqlite3" --file_type "8-K" -t 4
```

### Run specific jobs

These tasks can be executed once the database of filings is built.

#### Find event date

```bash
❯ edgar-analyzer find_event_date -h
usage: edgar-analyzer [OPTION]... find_event_date [-h] -d data_directory --file_type file_type [-db databsae] [-t threads]

Find event date from filings from header data

options:
  -h, --help            show this help message and exit
  -t threads, --threads threads
                        number of processes to use

required named arguments:
  -d data_directory, --data_dir data_directory
                        directory of filings
  --file_type file_type
                        type of filing
  -db databsae, --database databsae
                        sqlite database to store results
```

#### Find reported items

```bash
❯ edgar-analyzer find_reported_items -h
usage: edgar-analyzer [OPTION]... find_reported_items [-h] -d data_directory --file_type file_type [-db databsae] [-t threads]

Find reported items from filings from header data

options:
  -h, --help            show this help message and exit
  -t threads, --threads threads
                        number of processes to use

required named arguments:
  -d data_directory, --data_dir data_directory
                        directory of filings
  --file_type file_type
                        type of filing
  -db databsae, --database databsae
                        sqlite database to store results
```

#### more to be integrated

## Example

Just a simple example of the job `find_event_date`. Based on the 1,491,368 8K filings (2004-2022), the table below shows the reporting lags (date of filing minus date of event). 

We can find that _most_ filings are filed on the same day as the event reported, and that over 99.99% of filings are filed within 4 calendar days (SEC requires 4 business days).

| Filing lag   (calendar days) | Frequency | Percentage | Cumulative |
| ---------------------------- | --------- | ---------- | ---------- |
| 0                            | 1470089   | 98.57%     | 98.57%     |
| 1                            | 20761     | 1.39%      | 99.97%     |
| 2                            | 285       | 0.02%      | 99.98%     |
| 3                            | 89        | 0.01%      | 99.99%     |
| 4                            | 47        | 0.00%      | 99.99%     |
| 5                            | 26        | 0.00%      | 100.00%    |
| 6                            | 14        | 0.00%      | 100.00%    |
| 7                            | 6         | 0.00%      | 100.00%    |
| 8                            | 4         | 0.00%      | 100.00%    |
| 9                            | 3         | 0.00%      | 100.00%    |
| 10 or more                   | 44        | 0.00%      | 100.00%    |

## Note

This tool is a work in progress and breaking changes may be expected.

## Contact

If you identify any issue, please feel free to contact me at [mingze.gao@sydney.edu.au](mailto:mingze.gao@sydney.edu.au).
