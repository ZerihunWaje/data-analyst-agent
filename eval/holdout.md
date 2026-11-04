## Question: How many orders have been delivered?
```sql
SELECT COUNT(*) AS delivered_orders FROM orders WHERE order_status = 'delivered';
```

## Question: What was the revenue in November 2017?
```sql
SELECT ROUND(SUM(i.price), 2) AS revenue
FROM order_items i JOIN orders o ON i.order_id = o.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
  AND o.order_purchase_timestamp >= '2017-11-01'
  AND o.order_purchase_timestamp < '2017-12-01';
```

## Question: How many unique customers placed an order in 2018?
```sql
SELECT COUNT(DISTINCT c.customer_unique_id) AS customers
FROM customers c JOIN orders o ON c.customer_id = o.customer_id
WHERE year(o.order_purchase_timestamp) = 2018;
```

## Question: Which product category has the most products?
```sql
SELECT COALESCE(t.product_category_name_english, p.product_category_name) AS category,
       COUNT(*) AS products
FROM products p
LEFT JOIN product_category_name_translation t
       ON p.product_category_name = t.product_category_name
GROUP BY category ORDER BY products DESC LIMIT 1;
```

## Question: What is the average delivery time in days for customers in Sao Paulo state (SP)?
```sql
SELECT ROUND(AVG(date_diff('day', o.order_purchase_timestamp,
                           o.order_delivered_customer_date)), 1) AS avg_days
FROM orders o JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_state = 'SP'
  AND o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL;
```