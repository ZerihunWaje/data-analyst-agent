# Table: order_items

One row per item in an order. Grain: (order_id, order_item_id). One order can have many items.

## Columns
- order_id (VARCHAR): joins to orders.order_id
- - order_item_id (BIGINT): sequence number of the item within its order (1, 2, 3...). It is NOT a count: never SUM or AVG it.
- product_id (VARCHAR): joins to products.product_id
- seller_id (VARCHAR): joins to sellers.seller_id
- shipping_limit_date (TIMESTAMP): seller's deadline to hand item to carrier
- price (DOUBLE): item price, excluding freight
- freight_value (DOUBLE): shipping cost for this item

## Joins
- orders, order_payments, order_reviews ON order_id
- products ON product_id
- sellers ON seller_id

## Notes
- Use this table for product, category and seller sales: SUM(price).
- Number of items sold: COUNT(*).
- Never join with order_payments without aggregating one side first (join fan-out).
- - Items per order: COUNT(*) * 1.0 / COUNT(DISTINCT order_id).