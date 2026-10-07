SELECT city_name, revenue, estimated_rent, active_customers,
 ROUND(revenue * 1.0 / NULLIF(active_customers, 0), 2) AS revenue_per_customer,
 ROUND(estimated_rent * 1.0 / NULLIF(active_customers, 0), 2) AS rent_per_customer
FROM city_metrics ORDER BY revenue_per_customer DESC, city_id;
