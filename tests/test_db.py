import duckdb


def test_duckdb_runs_sql():
    con = duckdb.connect()  # in-memory database
    assert con.execute("SELECT 1 + 1").fetchone()[0] == 2