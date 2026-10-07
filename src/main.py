"""One entry point: validate data, execute SQL reports, export MySQL setup."""
import argparse
import csv
import json
from decimal import Decimal
from pathlib import Path
from data_loader import load_data
from database import build_sqlite, export_mysql

ROOT = Path(__file__).resolve().parents[1]


def run(data: Path, output: Path):
    tables = load_data(data)
    output.mkdir(parents=True, exist_ok=True)
    connection = build_sqlite(tables, ROOT / 'sql/00_schema.sql')
    summary = {'row_counts': {name: len(rows) for name, rows in tables.items()},
               'first_sale': min(row[1] for row in tables['sales']),
               'last_sale': max(row[1] for row in tables['sales']),
               'total_revenue': str(sum((row[5] for row in tables['sales']), Decimal(0)))}
    try:
        for query in sorted((ROOT / 'sql/analysis').glob('*.sql')):
            cursor = connection.execute(query.read_text())
            headings = [column[0] for column in cursor.description]
            records = cursor.fetchall()
            with (output / f'{query.stem}.csv').open('w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headings)
                writer.writerows(records)
            if query.stem == '10_expansion_shortlist':
                summary['shortlist'] = [dict(zip(headings, row)) for row in records]
        summary['q4_2023_revenue'] = connection.execute(
            "SELECT COALESCE(SUM(total),0) FROM sales WHERE sale_date >= '2023-10-01' AND sale_date < '2024-01-01'"
        ).fetchone()[0]
    finally:
        connection.close()
    export_mysql(tables, ROOT / 'sql/00_schema.sql', output / 'mysql_setup.sql')
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    print(f'Reports and MySQL setup written to {output.resolve()}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'data')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'outputs')
    args = parser.parse_args()
    try:
        run(args.data_dir, args.output_dir)
    except (ValueError, OSError) as error:
        parser.exit(1, f'Error: {error}\n')
