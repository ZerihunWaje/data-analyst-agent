# Table: products

One row per product. Grain: product_id.

## Columns
- product_id (VARCHAR): joins to order_items.product_id
- product_category_name (VARCHAR): category in PORTUGUESE, can be NULL
- product_name_lenght (BIGINT): length of product name. Note the spelling: "lenght", not "length".
- product_description_lenght (BIGINT): length of description. Spelled "lenght".
- product_photos_qty (BIGINT): number of photos
- product_weight_g (BIGINT): weight in grams
- product_length_cm, product_height_cm, product_width_cm (BIGINT): dimensions in cm

## Joins
- order_items ON product_id
- product_category_name_translation ON product_category_name

## Notes
- For English category names, join product_category_name_translation.
- Products have no price column. Price is in order_items.price.