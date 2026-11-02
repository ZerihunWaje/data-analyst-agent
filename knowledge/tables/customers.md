# Table: customers

One row per customer_id. Grain: customer_id, which is created PER ORDER.

## Columns
- customer_id (VARCHAR): key to orders.customer_id. One per order, NOT a unique person.
- customer_unique_id (VARCHAR): the real person. Use this to count customers.
- customer_zip_code_prefix (VARCHAR): first 5 digits of zip code, text (keeps leading zeros)
- customer_city (VARCHAR): city name, lowercase
- customer_state (VARCHAR): two-letter Brazilian state code, e.g. 'SP', 'RJ'

## Joins
- orders ON customers.customer_id = orders.customer_id

## Notes
- "How many customers": COUNT(DISTINCT customer_unique_id), never COUNT(customer_id).
- "Repeat customers": customer_unique_id with more than one order.