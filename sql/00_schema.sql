CREATE TABLE city (
 city_id INTEGER PRIMARY KEY,
 city_name VARCHAR(50) NOT NULL UNIQUE,
 population BIGINT NOT NULL CHECK (population > 0),
 estimated_rent DECIMAL(14,2) NOT NULL CHECK (estimated_rent >= 0),
 city_rank INTEGER NOT NULL
);
CREATE TABLE products (
 product_id INTEGER PRIMARY KEY,
 product_name VARCHAR(100) NOT NULL,
 price DECIMAL(14,2) NOT NULL CHECK (price >= 0),
 is_special INTEGER NOT NULL CHECK (is_special IN (0,1))
);
CREATE TABLE customers (
 customer_id INTEGER PRIMARY KEY,
 customer_name VARCHAR(100) NOT NULL,
 city_id INTEGER NOT NULL, FOREIGN KEY (city_id) REFERENCES city(city_id)
);
CREATE TABLE calendar_months (month_start DATE PRIMARY KEY);
CREATE TABLE sales (
 sale_id INTEGER PRIMARY KEY,
 sale_date DATE NOT NULL,
 month_start DATE NOT NULL,
 product_id INTEGER NOT NULL,
 customer_id INTEGER NOT NULL,
 total DECIMAL(14,2) NOT NULL CHECK (total >= 0),
 rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
 FOREIGN KEY (month_start) REFERENCES calendar_months(month_start),
 FOREIGN KEY (product_id) REFERENCES products(product_id),
 FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
CREATE INDEX idx_customers_city ON customers(city_id);
CREATE INDEX idx_sales_customer_month ON sales(customer_id, month_start);
CREATE INDEX idx_sales_product ON sales(product_id);
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE VIEW city_metrics AS
SELECT ci.city_id, ci.city_name, ci.population, ci.estimated_rent,
 COALESCE(SUM(s.total), 0) AS revenue,
 COUNT(DISTINCT s.customer_id) AS active_customers,
 COUNT(s.sale_id) AS sales_count
FROM city ci LEFT JOIN customers c ON c.city_id = ci.city_id
LEFT JOIN sales s ON s.customer_id = c.customer_id
GROUP BY ci.city_id, ci.city_name, ci.population, ci.estimated_rent;
