"""Read and validate source CSVs before anything is written to a database."""
import csv
import io
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from pathlib import Path

SPECIAL_PRODUCT_IDS = frozenset(range(21, 29))
COLUMNS = {
    'city': ['city_id', 'city_name', 'population', 'estimated_rent', 'city_rank'],
    'products': ['product_id', 'product_name', 'price', 'is_special'],
    'customers': ['customer_id', 'customer_name', 'city_id'],
    'calendar_months': ['month_start'],
    'sales': ['sale_id', 'sale_date', 'month_start', 'product_id', 'customer_id', 'total', 'rating'],
}


def read_rows(path: Path):
    raw = path.read_bytes()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('cp1252')
    reader = csv.DictReader(io.StringIO(text))
    expected = [c for c in COLUMNS[path.stem] if c not in {'is_special', 'month_start'}]
    headers = reader.fieldnames or []
    if [c for c in headers if c] != expected:
        raise ValueError(f'{path.name}: expected columns {expected}, got {headers}')
    for line, row in enumerate(reader, start=2):
        # The original sales export contains seven empty trailing columns.
        if any(value for key, value in row.items() if key not in expected):
            raise ValueError(f'{path.name}:{line}: unexpected non-empty column')
        if any(row.get(key) is None or not row[key].strip() for key in expected):
            raise ValueError(f'{path.name}:{line}: missing required value')
        yield line, {key: row[key].strip() for key in expected}


def money(value: str) -> Decimal:
    amount = Decimal(value)
    if not amount.is_finite() or amount < 0 or amount > Decimal('999999999999.99'):
        raise ValueError('invalid monetary amount')
    if amount != amount.quantize(Decimal('0.01')):
        raise ValueError('monetary amount has more than two decimal places')
    return amount


def load_data(directory: Path) -> dict:
    tables = {name: [] for name in COLUMNS}
    identifiers = {name: set() for name in ('city', 'products', 'customers', 'sales')}
    for table in identifiers:
        for line, row in read_rows(directory / f'{table}.csv'):
            try:
                identifier = int(row[{"city": "city_id", "products": "product_id", "customers": "customer_id", "sales": "sale_id"}[table]])
                if identifier <= 0 or identifier in identifiers[table]:
                    raise ValueError('non-positive or duplicate primary key')
                if table == 'city':
                    population = int(row['population'])
                    rent = money(row['estimated_rent'])
                    rank = int(row['city_rank'])
                    if population <= 0 or rank <= 0:
                        raise ValueError('population and rank must be positive')
                    record = [identifier, row['city_name'], population, rent, rank]
                elif table == 'products':
                    record = [identifier, row['product_name'], money(row['price']),
                              int(identifier in SPECIAL_PRODUCT_IDS)]
                elif table == 'customers':
                    city_id = int(row['city_id'])
                    if city_id not in identifiers['city']:
                        raise ValueError('unknown city_id')
                    record = [identifier, row['customer_name'], city_id]
                else:
                    sold_on = datetime.strptime(row['sale_date'], '%d-%m-%Y').date()
                    product_id, customer_id = int(row['product_id']), int(row['customer_id'])
                    rating = int(row['rating'])
                    if product_id not in identifiers['products'] or customer_id not in identifiers['customers']:
                        raise ValueError('unknown product_id or customer_id')
                    if not 1 <= rating <= 5:
                        raise ValueError('rating outside 1..5')
                    record = [identifier, sold_on.isoformat(), sold_on.replace(day=1).isoformat(),
                              product_id, customer_id, money(row['total']), rating]
                identifiers[table].add(identifier)
                tables[table].append(record)
            except (ValueError, InvalidOperation) as error:
                raise ValueError(f'{table}.csv:{line}: {error}') from error
    names = [row[1] for row in tables['city']]
    if len(names) != len(set(names)):
        raise ValueError('duplicate city names')
    if not tables['sales']:
        raise ValueError('sales.csv is empty')
    first = date.fromisoformat(min(row[2] for row in tables['sales']))
    last = date.fromisoformat(max(row[2] for row in tables['sales']))
    while first <= last:
        tables['calendar_months'].append([first.isoformat()])
        first = date(first.year + (first.month == 12), first.month % 12 + 1, 1)
    return tables
