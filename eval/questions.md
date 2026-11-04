## Question: How many customers are there?
```sql
SELECT COUNT(DISTINCT customer_unique_id) AS customers FROM customers;
```

## Question: What is the total revenue?
```sql
SELECT ROUND(SUM(i.price), 2) AS revenue
FROM order_items i JOIN orders o ON i.order_id = o.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable');
```

## Question: What was the revenue in 2017?
```sql
SELECT ROUND(SUM(i.price), 2) AS revenue
FROM order_items i JOIN orders o ON i.order_id = o.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
  AND year(o.order_purchase_timestamp) = 2017;
```

## Question: Which 3 product categories appear in the most order items?
```sql
SELECT COALESCE(t.product_category_name_english, p.product_category_name) AS category,
       COUNT(*) AS items
FROM order_items i
JOIN products p ON i.product_id = p.product_id
LEFT JOIN product_category_name_translation t
       ON p.product_category_name = t.product_category_name
GROUP BY category ORDER BY items DESC LIMIT 3;
```

## Question: What is the average review score?
```sql
SELECT ROUND(AVG(review_score), 2) AS avg_score FROM order_reviews;
```

## Question: What share of delivered orders arrived late?
```sql
SELECT AVG(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date
                THEN 1.0 ELSE 0.0 END) AS late_rate
FROM orders
WHERE order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL;
```

## Question: What is the average delivery time in days?
```sql
SELECT ROUND(AVG(date_diff('day', order_purchase_timestamp,
                           order_delivered_customer_date)), 1) AS avg_days
FROM orders
WHERE order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL;
```

## Question: How many orders were canceled?
```sql
SELECT COUNT(*) AS canceled_orders FROM orders WHERE order_status = 'canceled';
```

## Question: Which customer state generates the most revenue?
```sql
SELECT c.customer_state, ROUND(SUM(i.price), 2) AS revenue
FROM order_items i
JOIN orders o ON i.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY c.customer_state ORDER BY revenue DESC LIMIT 1;
```

## Question: What is the overall average order value?
```sql
SELECT ROUND(SUM(i.price) / COUNT(DISTINCT i.order_id), 2) AS avg_order_value
FROM order_items i JOIN orders o ON i.order_id = o.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable');
```

## Question: Which 5 states have the most sellers?
```sql
SELECT seller_state, COUNT(*) AS sellers
FROM sellers GROUP BY seller_state ORDER BY sellers DESC LIMIT 5;
```

## Question: How many customers placed more than one order?
```sql
SELECT COUNT(*) AS repeat_customers
FROM (
    SELECT c.customer_unique_id
    FROM customers c JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
    HAVING COUNT(DISTINCT o.order_id) >= 2
);
```

## Question: How much was paid in total by credit card?
```sql
SELECT ROUND(SUM(payment_value), 2) AS total_paid
FROM order_payments WHERE payment_type = 'credit_card';
```

## Question: Which month in 2017 had the most orders?
```sql
SELECT date_trunc('month', order_purchase_timestamp) AS month,
       COUNT(DISTINCT order_id) AS orders
FROM orders WHERE year(order_purchase_timestamp) = 2017
GROUP BY month ORDER BY orders DESC LIMIT 1;
```

## Question: What is the average freight cost per item?
```sql
SELECT ROUND(AVG(freight_value), 2) AS avg_freight FROM order_items;
```

## Question: How many products have no category?
```sql
SELECT COUNT(*) AS products_without_category
FROM products WHERE product_category_name IS NULL;
```

## Question: What is the average number of items per order?
```sql
SELECT ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT order_id), 2) AS items_per_order
FROM order_items;
```

## Question: What is the average review score for late deliveries?
```sql
SELECT ROUND(AVG(r.review_score), 2) AS avg_score
FROM order_reviews r JOIN orders o ON r.order_id = o.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date > o.order_estimated_delivery_date;
```

## Question: How much did customers pay in total, including freight?
```sql
SELECT ROUND(SUM(payment_value), 2) AS total_paid FROM order_payments;
```

## Question: Which 5 sellers sold the most items?
```sql
SELECT seller_id, COUNT(*) AS items_sold
FROM order_items GROUP BY seller_id ORDER BY items_sold DESC LIMIT 5;
```