import os

OUT = "C:/Users/35864/Desktop/全国大学生18届/mini-program/miniprogram/data"
os.makedirs(OUT, exist_ok=True)

# papers from SQLite
import sqlite3
DB = "C:/Users/35864/Desktop/全国大学生18届/db.sqlite3"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
import json

def dump(table, cols, name):
    cur = conn.execute(f"SELECT {cols} FROM {table}")
    rows = [dict(r) for r in cur.fetchall()]
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"{name}: {len(rows)} rows")
    return rows

# Check actual columns
cur = conn.execute("PRAGMA table_info(question_bank_paper)")
paper_cols = [r[1] for r in cur.fetchall()]
print("paper cols:", paper_cols)

cur = conn.execute("PRAGMA table_info(question_bank_question)")
q_cols = [r[1] for r in cur.fetchall()]
print("question cols:", q_cols)

cur = conn.execute("PRAGMA table_info(question_bank_knowledgepoint)")
kp_cols = [r[1] for r in cur.fetchall()]
print("kp cols:", kp_cols)

# Export papers
dump("question_bank_paper", ", ".join(paper_cols), "papers.json")

# Export questions (select useful cols)
q_useful = [c for c in q_cols if c in ["id", "question_no", "sort_order", "question_type", "score", "stem_md", "answer_md", "solution_md", "search_text", "source_page", "status", "paper_id"]]
print("q useful:", q_useful)
dump("question_bank_question", ", ".join(q_useful), "questions.json")

# Export knowledge points
kp_useful = [c for c in kp_cols if c in ["id", "name", "subject", "sort_order", "parent_id"]]
print("kp useful:", kp_useful)
dump("question_bank_knowledgepoint", ", ".join(kp_useful), "knowledge_points.json")

# Export qkp
dump("question_bank_questionknowledgepoint", "question_id, knowledge_point_id", "qkp.json")

conn.close()
print("Done.")