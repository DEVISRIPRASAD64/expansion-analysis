"""Database construction and MySQL script export; no analysis logic lives here."""
import sqlite3
from decimal import Decimal
from pathlib import Path
from data_loader import COLUMNS


def build_sqlite(tables: dict, schema: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(':memory:')
    connection.execute('PRAGMA foreign_keys = ON')
    connection.executescript(schema.read_text())
    with connection:
        for table, columns in COLUMNS.items():
            placeholders = ','.join('?' for _ in columns)
            rows = [[str(value) if isinstance(value, Decimal) else value for value in row]
                    for row in tables[table]]
            connection.executemany(
                f'INSERT INTO {table} ({",".join(columns)}) VALUES ({placeholders})', rows)
    return connection


def sql_literal(value):
    if isinstance(value, (int, Decimal)):
        return str(value)
    # NO_BACKSLASH_ESCAPES is set in the generated MySQL script.
    return "'" + str(value).replace("'", "''") + "'"


def export_mysql(tables: dict, schema: Path, destination: Path):
    with destination.open('w', encoding='utf-8') as output:
        output.write('-- Run against a NEW, EMPTY MySQL 8.0.16+ database.\n')
        output.write("SET NAMES utf8mb4;\nSET SESSION sql_mode = 'STRICT_TRANS_TABLES,ONLY_FULL_GROUP_BY,NO_BACKSLASH_ESCAPES';\n")
        output.write(schema.read_text() + '\nSTART TRANSACTION;\n')
        for table, columns in COLUMNS.items():
            rows = tables[table]
            for start in range(0, len(rows), 500):
                values = [ '(' + ','.join(sql_literal(v) for v in row) + ')' for row in rows[start:start+500]]
                output.write(f'INSERT INTO {table} ({",".join(columns)}) VALUES\n')
                output.write(',\n'.join(values) + ';\n')
        output.write('COMMIT;\n')
