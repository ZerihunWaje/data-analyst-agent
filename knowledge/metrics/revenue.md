# Metric: revenue

Definition: revenue = SUM(order_items.price). Product sales only, excludes freight.
Only count orders where order_status NOT IN ('canceled', 'unavailable').

## SQL pattern
SELECT SUM(i.price) AS revenue
FROM order_items i
JOIN orders o ON i.order_id = o.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable');

## Related metrics
- Revenue by category / product / seller: same formula, GROUP BY that dimension.
- Average order value (AOV): SUM(i.price) / COUNT(DISTINCT i.order_id).
- Total payments (what customers paid, incl. freight): SUM(order_payments.payment_value).
  Use only when the question asks about payments, not revenue.
- Revenue per month: GROUP BY date_trunc('month', o.order_purchase_timestamp).