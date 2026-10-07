SELECT ci.city_name, COALESCE(SUM(s.total), 0) AS revenue
FROM city ci LEFT JOIN customers c ON c.city_id = ci.city_id
LEFT JOIN sales s ON s.customer_id = c.customer_id
 AND s.sale_date >= '2023-10-01' AND s.sale_date < '2024-01-01'
GROUP BY ci.city_id, ci.city_name ORDER BY revenue DESC, ci.city_id;
