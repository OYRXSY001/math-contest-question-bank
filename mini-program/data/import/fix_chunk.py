import re, os

sql = open(r"C:/Users/35864/Desktop/全国大学生18届/mini-program/migrate_output.sql", encoding="utf-8").read()

# Extract knowledge_points INSERT lines
kp_lines = re.findall(r"INSERT INTO knowledge_points \(id[^\n]+;\n?", sql)

def get_id(line):
    m = re.search(r"VALUES\s*\((\d+)", line)
    return int(m.group(1)) if m else 0

kp_lines.sort(key=get_id)

print("Knowledge points order (id, parent):")
for line in kp_lines:
    id_val = get_id(line)
    # Extract parent_id: after VALUES(id, 'name', 'slug', 'subject', parent_id, sort_order)
    m = re.search(r"VALUES\s*\(\d+,\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*(NULL|\d+)", line)
    parent = m.group(1) if m else "?"
    print(f"  id={id_val}, parent={parent}")

# Extract papers
papers = re.findall(r"INSERT INTO papers \(id[^\n]+;\n?", sql)

combined = "\n".join(kp_lines) + "\n" + "\n".join(papers)

outdir = r"C:/Users/35864/Desktop/全国大学生18届/mini-program/data/import/chunks"
f1 = os.path.join(outdir, "01_kp_papers.sql")
with open(f1, "w", encoding="utf-8") as f:
    f.write(combined)

print(f"\nFile size: {len(combined)//1024} KB, lines: {len(combined.splitlines())}")