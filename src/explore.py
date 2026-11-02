import duckdb

from db import DB_PATH, get_schema

con = duckdb.connect(DB_PATH, read_only=True)
print(get_schema(con))
correct = con.execute(
    "SELECT ROUND(SUM(payment_value), 2) FROM order_payments"
).fetchone()[0]

fanned_out = con.execute(
    """
    SELECT ROUND(SUM(p.payment_value), 2)
    FROM order_payments p
    JOIN order_items i ON p.order_id = i.order_id
    """
).fetchone()[0]

print(f"Correct total revenue:  {correct:,}")
print(f"After joining items:    {fanned_out:,}")




con.close()