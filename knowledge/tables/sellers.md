# Table: sellers

One row per seller (merchant on the marketplace). Grain: seller_id.

## Columns
- seller_id (VARCHAR): joins to order_items.seller_id
- seller_zip_code_prefix (VARCHAR): first 5 digits of zip code
- seller_city (VARCHAR): city name, lowercase
- seller_state (VARCHAR): two-letter Brazilian state code, e.g. 'SP'

## Joins
- order_items ON seller_id

## Notes
- Sellers connect to orders only through order_items.
- Seller revenue: SUM(order_items.price) grouped by seller_id.