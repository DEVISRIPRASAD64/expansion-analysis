WITH monthly AS (
 SELECT ci.city_id, ci.city_name, m.month_start, COALESCE(SUM(s.total), 0) AS revenue
 FROM city ci CROSS JOIN calendar_months m
 LEFT JOIN customers c ON c.city_id = ci.city_id
 LEFT JOIN sales s ON s.customer_id = c.customer_id AND s.month_start = m.month_start
 GROUP BY ci.city_id, ci.city_name, m.month_start
), previous AS (
 SELECT monthly.*, LAG(revenue) OVER (
 PARTITION BY city_id ORDER BY month_start) AS previous_revenue FROM monthly
)
SELECT city_name, month_start, revenue, previous_revenue,
 ROUND((revenue - previous_revenue) * 100.0 / NULLIF(previous_revenue, 0), 2) AS growth_percent
FROM previous ORDER BY city_id, month_start;
