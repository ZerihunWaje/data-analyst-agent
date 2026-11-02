# Metric: customers and orders

- Number of customers: COUNT(DISTINCT customers.customer_unique_id).
  Never COUNT(customer_id): customer_id is created per order.
- Number of orders: COUNT(DISTINCT orders.order_id).
- Repeat customer: a customer_unique_id with 2 or more orders.
- Customers per state: GROUP BY customers.customer_state.

## SQL pattern: repeat customers
SELECT COUNT(*) AS repeat_customers
FROM (
    SELECT c.customer_unique_id
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
    HAVING COUNT(DISTINCT o.order_id) >= 2
);