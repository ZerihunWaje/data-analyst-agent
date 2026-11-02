import duckdb

from db import DB_PATH

con = duckdb.connect(DB_PATH, read_only=True)

late_rate = con.execute(
    """
    SELECT AVG(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date
                    THEN 1.0 ELSE 0.0 END) AS late_rate
    FROM orders
    WHERE order_status = 'delivered'
      AND order_delivered_customer_date IS NOT NULL
    """
).fetchone()[0]

print(f"Late delivery rate: {late_rate:.1%}")

con.close()