# Metric: delivery performance

Only delivered orders: order_status = 'delivered' AND order_delivered_customer_date IS NOT NULL.

- Delivery time (days): date_diff('day', order_purchase_timestamp, order_delivered_customer_date)
- Late delivery: order_delivered_customer_date > order_estimated_delivery_date
- Late delivery rate: share of delivered orders that were late.

## SQL pattern: late delivery rate
SELECT AVG(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date
                THEN 1.0 ELSE 0.0 END) AS late_rate
FROM orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL;