# 317 Pizzas — Expansion Analysis

A readable replica of https://github.com/kal-el95/Expansion-Analysis using its four original CSV datasets. SQL answers the business questions; a small Python runner handles validation, loading and report exports. No pip packages are required.

## Run in two commands

Requires Python 3.10 or newer. Open a terminal inside this folder:

```bash
python3 src/main.py
python3 -m unittest discover -s tests -v
```

On Windows, use `py` in place of `python3` if needed. Output goes to `outputs/`: ten CSV reports, `summary.json`, and `mysql_setup.sql`. Input CSVs are read only. Each run uses a fresh in-memory SQLite database and replaces the generated output files. To keep an earlier run, specify a separate directory:

```bash
python3 src/main.py --output-dir outputs/new_run
```

## Run the same analysis in MySQL

Use MySQL **8.0.16 or newer** for enforced CHECK constraints and window functions. First run the Python command to produce the cleaned import script. It preserves monetary values as decimal literals and converts `DD-MM-YYYY` dates to ISO dates.

In MySQL Workbench:

1. Connect to your server and create a **new empty database**:
   `CREATE DATABASE pizza_expansion CHARACTER SET utf8mb4;`
2. Run `USE pizza_expansion;` and then open and execute `outputs/mysql_setup.sql`.
3. Open any file in `sql/analysis/` and run it with `pizza_expansion` selected.

Alternatively, from a terminal:

```bash
mysql -u root -p -e "CREATE DATABASE pizza_expansion CHARACTER SET utf8mb4;"
mysql -u root -p pizza_expansion < outputs/mysql_setup.sql
mysql -u root -p pizza_expansion < sql/analysis/10_expansion_shortlist.sql
```

The script creates tables and indexes before inserting data in a transaction. It never drops tables. Use a fresh database for a repeat import; MySQL DDL commits independently, so an interrupted import can leave created tables behind. The import sets strict SQL mode, UTF-8 and `NO_BACKSLASH_ESCAPES` for its session; do not remove those lines. No passwords are stored in the project.

The SQL is shared between MySQL and SQLite. Automated execution was verified with SQLite; a live MySQL server was unavailable in the build environment. SQLite's NUMERIC affinity can use floating point for fractional amounts, while MySQL DECIMAL preserves fixed precision. The supplied monetary dataset consists of integer amounts, and its totals were reconciled independently using Python Decimal.

## Layout

| Path | Responsibility |
|---|---|
| `data/` | Unmodified original CSV exports |
| `src/data_loader.py` | Encoding cleanup, date parsing, validation, month calendar |
| `src/database.py` | SQLite loading and MySQL import generation |
| `src/main.py` | Runs SQL files and exports reports |
| `sql/00_schema.sql` | Tables, constraints, indexes, reusable city metrics view |
| `sql/analysis/` | Ten numbered, independently readable business queries |
| `tests/` | Reconciliation, date boundaries, ranking and edge cases |
| `docs/` | Architecture, SQL learning guide and interpretation |
| `outputs/` | Reproducible reports and cleaned MySQL import |

## Verified findings

There are **14 cities, 28 products, 497 registered customers and 10,388 sales**. The observed date range is **1 January 2023–1 October 2024**. Total recorded revenue is **₹6,070,190**; Q4 2023 revenue is **₹1,963,300**.

| Revenue rank | City | Recorded revenue | Purchasing customers | Revenue/customer |
|---|---|---:|---:|---:|
| 1 | Pune | ₹1,258,290 | 52 | ₹24,197.88 |
| 2 | Chennai | ₹944,120 | 42 | ₹22,479.05 |
| 3 | Bangalore | ₹860,110 | 39 | ₹22,054.10 |

These are the top three **by historical revenue**, not a forecast of profitable store openings. The original README recommends Pune, Delhi and Jaipur; its SQL does not define a scoring rule that reproduces that selection. This version makes its ranking rule explicit instead of copying that recommendation as a calculated result.

See [interpretation](docs/interpretation.md) before presenting findings. See [architecture](docs/architecture.md) and [SQL walkthrough](docs/sql_walkthrough.md) to understand the implementation.

## Source attribution

The input data and original business questions come from `kal-el95/Expansion-Analysis` (uploaded snapshot commit `2b7f6f0933cdee02089e00079726b265ccf98dc8`). New implementation files reorganize and adapt those questions. The supplied snapshot contained no LICENSE file; this project does not assign a new license to the source data. Check upstream permissions before redistributing it publicly.
