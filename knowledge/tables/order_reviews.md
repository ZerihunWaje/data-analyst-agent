# Table: order_reviews

Customer review of an order. Grain: one review per row; most orders have one review, some have none.

## Columns
- review_id (VARCHAR): review identifier
- order_id (VARCHAR): joins to orders.order_id
- review_score (BIGINT): rating from 1 (worst) to 5 (best)
- review_comment_title (VARCHAR): optional, often NULL, Portuguese
- review_comment_message (VARCHAR): optional, often NULL, Portuguese
- review_creation_date (TIMESTAMP): when the review survey was sent
- review_answer_timestamp (TIMESTAMP): when the customer answered

## Joins
- orders ON order_id

## Notes
- Average rating: AVG(review_score).
- Not every order has a review: use LEFT JOIN from orders if all orders must be kept.