# Table: order_payments

One row per payment method used in an order. Grain: (order_id, payment_sequential).
An order paid with a voucher plus a credit card has two rows.

## Columns
- order_id (VARCHAR): joins to orders.order_id
- payment_sequential (BIGINT): sequence number of the payment within the order
- payment_type (VARCHAR): credit_card, boleto, voucher, debit_card, not_defined
- payment_installments (BIGINT): number of installments chosen
- payment_value (DOUBLE): amount paid, includes freight

## Joins
- orders ON order_id

## Notes
- Use this table for total revenue / what customers paid: SUM(payment_value).
- Do not join with order_items before aggregating payments per order (join fan-out).
- boleto is a Brazilian bank slip payment method.