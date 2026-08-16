import os
import re

CHUNK_DIR = "C:/Users/35864/Desktop/全国大学生18届/mini-program/data/import/chunks2"
OUT_DIR = os.path.join(CHUNK_DIR, "split")
os.makedirs(OUT_DIR, exist_ok=True)

files_to_split = [
    "02_questions_11.sql",
    "02_questions_12.sql",
    "02_questions_13.sql",
]

MAX_SIZE = 20000  # 20KB per sub-chunk

for fname in files_to_split:
    fpath = os.path.join(CHUNK_DIR, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        sql = f.read()

    # Split by INSERT statements
    inserts = re.split(r'(?=INSERT INTO questions)', sql)
    inserts = [s.strip() for s in inserts if s.strip()]

    base = fname.replace(".sql", "")
    sub_idx = 1
    current = []
    current_size = 0

    for ins in inserts:
        ins_size = len(ins.encode("utf-8"))
        if current_size + ins_size > MAX_SIZE and current:
            outpath = os.path.join(OUT_DIR, f"{base}_part{sub_idx:02d}.sql")
            with open(outpath, "w", encoding="utf-8") as f:
                f.write("; ".join(current) + ";")
            print(f"  {outpath}: {current_size} bytes, {len(current)} inserts")
            current = []
            current_size = 0
            sub_idx += 1
        current.append(ins)
        current_size += ins_size + 2

    if current:
        outpath = os.path.join(OUT_DIR, f"{base}_part{sub_idx:02d}.sql")
        with open(outpath, "w", encoding="utf-8") as f:
            f.write("; ".join(current) + ";")
        print(f"  {outpath}: {current_size} bytes, {len(current)} inserts")

print("\nDone. Files:")
for f in sorted(os.listdir(OUT_DIR)):
    fpath = os.path.join(OUT_DIR, f)
    print(f"  {f}: {os.path.getsize(fpath)} bytes")