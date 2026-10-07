SELECT city_name, population, ROUND(population * 0.25, 0) AS estimated_consumers,
 active_customers, ROUND(active_customers * 100.0 / NULLIF(population * 0.25, 0), 4) AS reach_percent
FROM city_metrics ORDER BY estimated_consumers DESC, city_id;
