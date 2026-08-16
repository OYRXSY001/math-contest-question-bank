import sqlite3
import os

DB_PATH = "C:/Users/35864/Desktop/全国大学生18届/db.sqlite3"

missing_ids = [30,31,32,33,34,35,36,37,38,39,40,41,44,45,46,47,48,49,50,51,52,53,54,
               93,94,95,96,97,98,99,100,105,106,107,108,109,110,111,112,113,114,115,116,
               117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,
               135,136,137,138,139,140,141,142,143,148,149,150,151,152,153,154,155,156,157]

# PG table columns in order
pg_cols = ["id", "paper_id", "question_no", "sort_order", "question_type", "score",
           "stem_md", "answer_md", "solution_md", "search_text", "source_page", "status"]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

placeholders = ",".join(["?"] * len(missing_ids))
cols_sql = ", ".join(pg_cols)
cur.execute(f"SELECT {cols_sql} FROM question_bank_question WHERE id IN ({placeholders}) ORDER BY id", missing_ids)
rows = cur.fetchall()
print(f"Found {len(rows)} questions")

not_found = set(missing_ids) - {r[0] for r in rows}
if not_found:
    print(f"NOT in SQLite: {sorted(not_found)}")

def esc(s):
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"

sql_lines = []
for row in rows:
    vals = ", ".join(esc(v) for v in row)
    cols_str = ", ".join(pg_cols)
    sql_lines.append(
        f"INSERT INTO questions ({cols_str}) VALUES ({vals}) ON CONFLICT (id) DO NOTHING;"
    )

# Split into chunks of ~5 questions each to stay under CLI arg limits
chunk_size = 5
out_dir = "C:/Users/35864/Desktop/全国大学生18届/mini-program/data/import/chunks2/fix_chunks"
os.makedirs(out_dir, exist_ok=True)

for i in range(0, len(sql_lines), chunk_size):
    chunk = sql_lines[i:i+chunk_size]
    chunk_path = os.path.join(out_dir, f"fix_{i//chunk_size + 1:02d}.sql")
    with open(chunk_path, "w", encoding="utf-8") as f:
        f.write("\n".join(chunk))
    print(f"  {os.path.basename(chunk_path)}: {os.path.getsize(chunk_path)} bytes, {len(chunk)} inserts")

conn.close()