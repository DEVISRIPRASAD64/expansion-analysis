SELECT p.product_id, p.product_name, COUNT(s.sale_id) AS sales_count,
 COALESCE(SUM(s.total), 0) AS revenue
FROM products p LEFT JOIN sales s ON s.product_id = p.product_id
GROUP BY p.product_id, p.product_name ORDER BY sales_count DESC, p.product_id;
