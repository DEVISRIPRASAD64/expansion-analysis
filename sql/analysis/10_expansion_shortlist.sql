SELECT city_name, revenue, estimated_rent, active_customers,
 ROUND(population * 0.25, 0) AS estimated_consumers,
 ROUND(revenue * 1.0 / NULLIF(active_customers, 0), 2) AS revenue_per_customer,
 ROUND(estimated_rent * 1.0 / NULLIF(active_customers, 0), 2) AS rent_per_customer
FROM city_metrics WHERE active_customers > 0
ORDER BY revenue DESC, city_id LIMIT 3;
