SELECT city_name, revenue, active_customers,
 ROUND(revenue * 1.0 / NULLIF(active_customers, 0), 2) AS revenue_per_customer
FROM city_metrics ORDER BY revenue DESC, city_id;
