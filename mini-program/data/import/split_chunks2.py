import re, os

sql = open(r"C:/Users/35864/Desktop/全国大学生18届/mini-program/migrate_output.sql", encoding="utf-8").read()

# Split DML by table
lines = sql.splitlines()
insert_start = None
for i, line in enumerate(lines):
    if line.strip().startswith("INSERT INTO knowledge_points"):
        insert_start = i
        break

dml = "\n".join(lines[insert_start:])

# Group by table
inserts = list(re.finditer(r"INSERT INTO (\w+)", dml))
table_chunks = {}
for i, m in enumerate(inserts):
    table = m.group(1)
    start = m.start()
    end = inserts[i+1].start() if i+1 < len(inserts) else len(dml)
    chunk = dml[start:end].strip()
    table_chunks.setdefault(table, []).append(chunk)

outdir = r"C:\Users\35864\Desktop\全国大学生18届\mini-program\data\import\chunks2"
os.makedirs(outdir, exist_ok=True)

chunk_files = []
MAX_KB = 25  # 每块不超过 25KB

# 1. knowledge_points + papers (small, ~23KB)
small = "\n".join(table_chunks["knowledge_points"]) + "\n" + "\n".join(table_chunks["papers"])
f1 = os.path.join(outdir, "01_kp_papers.sql")
with open(f1, "w", encoding="utf-8") as f:
    f.write(small)
chunk_files.append(f1)

# 2. questions: split into smaller batches
q_lines = table_chunks["questions"]
batch = []
batch_size = 0
batch_num = 1
for line in q_lines:
    if batch_size + len(line) > MAX_KB * 1024 and batch:
        fn = os.path.join(outdir, f"02_questions_{batch_num}.sql")
        with open(fn, "w", encoding="utf-8") as f:
            f.write("\n".join(batch))
        chunk_files.append(fn)
        batch = [line]
        batch_size = len(line)
        batch_num += 1
    else:
        batch.append(line)
        batch_size += len(line)
if batch:
    fn = os.path.join(outdir, f"02_questions_{batch_num}.sql")
    with open(fn, "w", encoding="utf-8") as f:
        f.write("\n".join(batch))
    chunk_files.append(fn)

# 3. question_knowledge_points: split into smaller batches
qkp_lines = table_chunks["question_knowledge_points"]
batch = []
batch_size = 0
batch_num = 1
for line in qkp_lines:
    if batch_size + len(line) > MAX_KB * 1024 and batch:
        fn = os.path.join(outdir, f"03_qkp_{batch_num}.sql")
        with open(fn, "w", encoding="utf-8") as f:
            f.write("\n".join(batch))
        chunk_files.append(fn)
        batch = [line]
        batch_size = len(line)
        batch_num += 1
    else:
        batch.append(line)
        batch_size += len(line)
if batch:
    fn = os.path.join(outdir, f"03_qkp_{batch_num}.sql")
    with open(fn, "w", encoding="utf-8") as f:
        f.write("\n".join(batch))
    chunk_files.append(fn)

for f in sorted(chunk_files):
    size = os.path.getsize(f)
    print(f"{os.path.basename(f)}: {size//1024}KB")
print(f"\nTotal chunks: {len(chunk_files)}")