# Table: product_category_name_translation

Lookup table: Portuguese category name to English. 71 rows.

## Columns
- product_category_name (VARCHAR): Portuguese name, joins to products.product_category_name
- product_category_name_english (VARCHAR): English name

## Joins
- products ON product_category_name

## Notes
- Use LEFT JOIN: a few categories have no translation, and some products have NULL category.
- Show the English name: COALESCE(product_category_name_english, product_category_name).