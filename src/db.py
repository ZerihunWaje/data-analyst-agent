from pathlib import Path

import duckdb

DATA_DIR = Path("data")
DB_PATH = "olist.duckdb"


def table_name(csv_path: Path) -> str:
    # olist_orders_dataset.csv -> orders
    return csv_path.stem.removeprefix("olist_").removesuffix("_dataset")


def load_csvs(con: duckdb.DuckDBPyConnection) -> None:
    for csv in sorted(DATA_DIR.glob("*.csv")):
        name = table_name(csv)
        con.execute(
            f"CREATE OR REPLACE TABLE {name} AS "
            f"SELECT * FROM read_csv_auto('{csv.as_posix()}')"
        )
        rows = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        print(f"{name:35} {rows:>8,} rows")

def get_schema(con: duckdb.DuckDBPyConnection) -> str:
    rows = con.execute(
        """
          SELECT table_name,column_name,data_type
          FROM information_schema.columns
          ORDER BY table_name,ordinal_position
        """

    ).fetchall()
    lines,current = [], None
    for table, column, dtype in rows:
        if table != current:
            lines.append(f"\n{table}")
            current=table
        lines.append(f"   {column}: {dtype}")
    return "\n".join(lines)
    
if __name__ == "__main__":
    con = duckdb.connect(DB_PATH)
    load_csvs(con)
    con.close()