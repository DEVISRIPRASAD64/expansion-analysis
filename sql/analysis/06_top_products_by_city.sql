WITH product_counts AS (
 SELECT ci.city_id, ci.city_name, p.product_id, p.product_name, COUNT(*) AS sales_count
 FROM sales s JOIN customers c ON c.customer_id = s.customer_id
 JOIN city ci ON ci.city_id = c.city_id JOIN products p ON p.product_id = s.product_id
 GROUP BY ci.city_id, ci.city_name, p.product_id, p.product_name
), ranked AS (
 SELECT product_counts.*, ROW_NUMBER() OVER (
 PARTITION BY city_id ORDER BY sales_count DESC, product_id) AS product_rank
 FROM product_counts
)
SELECT city_name, product_name, sales_count, product_rank FROM ranked
WHERE product_rank <= 3 ORDER BY city_id, product_rank;
