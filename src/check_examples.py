import re
import sys
from pathlib import Path

import duckdb

from db import DB_PATH

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("knowledge/examples/examples.md")
text = path.read_text(encoding="utf-8")

sql_blocks = re.findall(r"```sql\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)  # CHANGED

if not sql_blocks:  # NEW
    raise ValueError(f"No ```sql blocks found ({len(text)} characters read)")  # NEW

con = duckdb.connect(DB_PATH, read_only=True)
for i, sql in enumerate(sql_blocks, 1):
    try:
        df = con.execute(sql).df()
        print(f"[OK]   example {i}: {len(df)} rows")
    except duckdb.Error as e:
        print(f"[FAIL] example {i}: {e}")

con.close()