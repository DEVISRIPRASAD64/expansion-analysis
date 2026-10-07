# SQL walkthrough

Read `00_schema.sql` first, then work through the analysis files in numerical order. Each query is a standalone report after schema and data setup.

| File | Business question | Main SQL concepts |
|---|---|---|
| 01 | Estimated potential consumers by city | Arithmetic, ROUND, ORDER BY |
| 02 | Q4 2023 revenue by city | LEFT JOIN, SUM, date interval |
| 03 | Recorded sales by product | COUNT(non-null key), GROUP BY |
| 04 | Revenue per purchasing customer | View, DISTINCT denominator, NULLIF |
| 05 | Observed customer reach | Population assumption, percentage |
| 06 | Exactly three most sold products per city | CTE, ROW_NUMBER, PARTITION BY |
| 07 | Customers purchasing special products | Conditional COUNT(DISTINCT CASE...) |
| 08 | Revenue/customer and rent/customer | Ratios, zero-safe division |
| 09 | Month-over-month revenue change | Month calendar, CROSS JOIN, LAG |
| 10 | Three cities with most recorded revenue | Reusable metrics, deterministic ORDER BY, LIMIT |

## The join path

To attach a city to a sale, join `sales.customer_id = customers.customer_id`, then `customers.city_id = city.city_id`. To attach a product, join `sales.product_id = products.product_id`. One customer can have many sales; SUM should add all sale totals, while customer counts must use COUNT(DISTINCT customer_id).

## Revenue per customer

The denominator is the number of customers who actually purchased, not all registered customers. `SUM(total) / COUNT(DISTINCT sales.customer_id)` is cumulative revenue per purchaser. `AVG(total)` would instead average sale amounts. `NULLIF(active_customers, 0)` makes the result NULL when there are no purchasers. Multiplying by 1.0 avoids SQLite integer truncation; MySQL DECIMAL handles decimal division.

## LEFT JOIN and filters

A Q4 date condition in WHERE would remove a zero-sale city's NULL joined row. Putting the condition in the sales JOIN preserves every city. COUNT(sale_id) counts zero when no match exists; COUNT(*) would count the preserved placeholder row.

## Ranking

The product query first counts rows per city and product. ROW_NUMBER then assigns an order within each city by sales count descending and product ID ascending. Filtering to rank <= 3 returns exactly three available products, with a deterministic choice among ties.

## Growth

The month calendar is crossed with cities to establish every city-month combination. Sales are LEFT JOINed and absent totals become zero. LAG(revenue) fetches the immediately preceding calendar month's total, partitioned by city. Growth is `(current - previous) / previous * 100`. The first month and any month following zero revenue have NULL growth.

## Useful exercises

1. Change Q4 2023 to Q1 2024 using two date boundaries.
2. Return three rank tiers with DENSE_RANK and compare tied products.
3. Compare registered customers with active purchasing customers.
4. Add a revenue-based product ranking beside the volume-based ranking.
5. Add a complete-year date filter to city metrics and compare the shortlist.
6. Explain why rent/customer and revenue/customer cannot directly establish profit.
