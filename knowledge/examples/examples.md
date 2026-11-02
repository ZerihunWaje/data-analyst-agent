## Question: How many orders were placed in 2017?
```sql
SELECT COUNT(DISTINCT order_id) AS orders
FROM orders
WHERE year(order_purchase_timestamp) = 2017;
```

## Question: What are the top 5 product categories by revenue?
```sql
SELECT COALESCE(t.product_category_name_english, p.product_category_name) AS category,
       ROUND(SUM(i.price), 2) AS revenue
FROM order_items i
JOIN orders o ON i.order_id = o.order_id
JOIN products p ON i.product_id = p.product_id
LEFT JOIN product_category_name_translation t
       ON p.product_category_name = t.product_category_name
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY category
ORDER BY revenue DESC
LIMIT 5;
```

## Question: Show monthly revenue in 2018.
```sql
SELECT date_trunc('month', o.order_purchase_timestamp) AS month,
       ROUND(SUM(i.price), 2) AS revenue
FROM order_items i
JOIN orders o ON i.order_id = o.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
  AND year(o.order_purchase_timestamp) = 2018
GROUP BY month
ORDER BY month;
```

## Question: What is the average review score by customer state?
```sql
SELECT c.customer_state,
       ROUND(AVG(r.review_score), 2) AS avg_score,
       COUNT(*) AS reviews
FROM order_reviews r
JOIN orders o ON r.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_state
ORDER BY avg_score DESC;
```

## Question: Which 5 states have the most customers?
```sql
SELECT customer_state,
       COUNT(DISTINCT customer_unique_id) AS customers
FROM customers
GROUP BY customer_state
ORDER BY customers DESC
LIMIT 5;
```

## Question: What share of payments uses each payment type?
```sql
SELECT payment_type,
       COUNT(*) AS payments,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM order_payments
GROUP BY payment_type
ORDER BY payments DESC;
```

## Question: What is the average delivery time in days per customer state?
```sql
SELECT c.customer_state,
       ROUND(AVG(date_diff('day', o.order_purchase_timestamp,
                           o.order_delivered_customer_date)), 1) AS avg_days
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY avg_days DESC;
```

## Question: Who are the top 10 sellers by revenue?
```sql
SELECT i.seller_id, s.seller_state,
       ROUND(SUM(i.price), 2) AS revenue
FROM order_items i
JOIN orders o ON i.order_id = o.order_id
JOIN sellers s ON i.seller_id = s.seller_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY i.seller_id, s.seller_state
ORDER BY revenue DESC
LIMIT 10;
```

## Question: What is the average order value per month?
```sql
SELECT date_trunc('month', o.order_purchase_timestamp) AS month,
       ROUND(SUM(i.price) / COUNT(DISTINCT i.order_id), 2) AS avg_order_value
FROM order_items i
JOIN orders o ON i.order_id = o.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY month
ORDER BY month;
```

## Question: What percentage of customers ordered more than once?
```sql
WITH per_customer AS (
    SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS n_orders
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
)
SELECT ROUND(100.0 * AVG(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END), 2) AS repeat_pct
FROM per_customer;
```

## Question: How much did customers pay in total per order status?
```sql
WITH order_paid AS (
    SELECT order_id, SUM(payment_value) AS paid
    FROM order_payments
    GROUP BY order_id
)
SELECT o.order_status, ROUND(SUM(op.paid), 2) AS total_paid
FROM orders o
JOIN order_paid op ON o.order_id = op.order_id
GROUP BY o.order_status
ORDER BY total_paid DESC;
```