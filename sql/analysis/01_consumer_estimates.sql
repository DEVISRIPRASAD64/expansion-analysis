SELECT city_name, population, ROUND(population * 0.25, 0) AS estimated_consumers,
 ROUND(population * 0.25 / 1000000, 2) AS consumers_millions
FROM city ORDER BY estimated_consumers DESC, city_id;
