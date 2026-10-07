SELECT ci.city_name, COUNT(DISTINCT CASE WHEN p.is_special = 1
 THEN s.customer_id END) AS special_customers
FROM city ci LEFT JOIN customers c ON c.city_id = ci.city_id
LEFT JOIN sales s ON s.customer_id = c.customer_id
LEFT JOIN products p ON p.product_id = s.product_id
GROUP BY ci.city_id, ci.city_name ORDER BY special_customers DESC, ci.city_id;
