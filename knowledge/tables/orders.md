# Table: orders

Central table of the database. One row per order (grain: order_id).
Almost every other table joins to orders via order_id.

## Columns
- order_id (VARCHAR): unique order identifier, primary key
- customer_id (VARCHAR): joins to customers.customer_id. Created per order, so it is NOT a unique person.
- order_status (VARCHAR): delivered, shipped, canceled, unavailable, invoiced, processing, created, approved
- order_purchase_timestamp (TIMESTAMP): when the order was placed. Use this for "orders per month" and time trends.
- order_delivered_customer_date (TIMESTAMP): actual delivery date, NULL if not delivered
- order_estimated_delivery_date (TIMESTAMP): promised delivery date

## Joins
- customers ON orders.customer_id = customers.customer_id
- order_items, order_payments, order_reviews ON order_id

## Notes
- For revenue or sales questions, usually filter order_status = 'delivered'.
- Do not join order_items and order_payments together without aggregating first (join fan-out).