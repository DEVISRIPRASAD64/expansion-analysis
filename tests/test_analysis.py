import csv
import shutil
import sqlite3
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from data_loader import load_data
from database import build_sqlite


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = load_data(ROOT / 'data')

    def setUp(self):
        self.connection = build_sqlite(self.tables, ROOT / 'sql/00_schema.sql')

    def tearDown(self):
        self.connection.close()

    def query(self, number):
        path = next((ROOT / 'sql/analysis').glob(f'{number:02}_*.sql'))
        return self.connection.execute(path.read_text()).fetchall()

    def test_revenue_reconciles_to_independent_csv_total(self):
        expected = sum((row[5] for row in self.tables['sales']), Decimal(0))
        actual = self.connection.execute('SELECT SUM(total) FROM sales').fetchone()[0]
        self.assertEqual(Decimal(str(actual)), expected)
        self.assertEqual(sum(row[3] for row in self.query(3)), actual)
        self.assertEqual(sum(row[1] for row in self.query(4)), actual)

    def test_q4_date_boundaries_match_csv(self):
        expected = sum((row[5] for row in self.tables['sales']
                        if '2023-10-01' <= row[1] < '2024-01-01'), Decimal(0))
        self.assertEqual(Decimal(str(sum(row[1] for row in self.query(2)))), expected)

    def test_top_three_and_per_city_product_limit(self):
        self.assertEqual([row[0] for row in self.query(10)], ['Pune', 'Chennai', 'Bangalore'])
        counts = {}
        for city, _, _, rank in self.query(6):
            counts[city] = counts.get(city, 0) + 1
            self.assertLessEqual(rank, 3)
        self.assertTrue(all(count == 3 for count in counts.values()))

    def test_missing_months_zero_denominators_and_inactive_city(self):
        tables = {
            'city': [[1, 'Active', 1000, Decimal('100'), 1], [2, 'Inactive', 1000, Decimal('50'), 2]],
            'products': [[1, 'Plain', Decimal('100'), 0]],
            'customers': [[1, 'Customer', 1]],
            'calendar_months': [['2023-01-01'], ['2023-02-01'], ['2023-03-01']],
            'sales': [[1, '2023-01-01', '2023-01-01', 1, 1, Decimal('100'), 5],
                      [2, '2023-03-01', '2023-03-01', 1, 1, Decimal('200'), 5]],
        }
        self.connection.close()
        self.connection = build_sqlite(tables, ROOT / 'sql/00_schema.sql')
        growth = [row for row in self.query(9) if row[0] == 'Active']
        self.assertEqual(growth[1][2:], (0, 100, -100.0))
        self.assertEqual(growth[2][3:], (0, None))
        inactive = [row for row in self.query(4) if row[0] == 'Inactive'][0]
        self.assertEqual(inactive[1:], (0, 0, None))
        self.assertEqual(self.query(7), [('Active', 0), ('Inactive', 0)])

    def test_unknown_foreign_key_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute("INSERT INTO customers VALUES (9999,'Unknown',9999)")

    def test_duplicate_source_sale_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            for source in (ROOT / 'data').glob('*.csv'):
                shutil.copyfile(source, directory / source.name)
            with (directory / 'sales.csv').open(newline='') as file:
                rows = list(csv.reader(file))
            with (directory / 'sales.csv').open('a', newline='') as file:
                csv.writer(file).writerow(rows[1])
            with self.assertRaisesRegex(ValueError, 'duplicate primary key'):
                load_data(directory)


if __name__ == '__main__':
    unittest.main()
