"""
SQLite → CloudBase PostgreSQL 数据迁移脚本
使用方法：
  1. 确保已启动 Django 项目且数据库可访问
  2. 运行：python data/import/migrate_to_pg.py
  3. 脚本输出 migrate_output.sql，用 managePgDatabase 执行即可

⚠️ 注意：此脚本读取本地 Django 数据库，不涉及 CloudBase API 调用。
   SQL 文件生成后，在管理后台用 `managePgDatabase` 执行。
"""
import os
import sys
import json

# 确保项目根目录在 sys.path 中
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, project_root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("DJANGO_DEBUG", "1")
import django
django.setup()

from question_bank.models import Paper, Question, KnowledgePoint, QuestionKnowledgePoint, Favorite, WrongQuestion


def escape(s):
    """转义 SQL 字符串"""
    if s is None:
        return ""
    return s.replace("'", "''").replace("\n", "\\n").replace("\r", "\\r")


def build_sql():
    lines = []

    # ============ 建表 ============
    lines.append("-- ====== 建表 ======\n")

    lines.append("""
CREATE TABLE IF NOT EXISTS papers (
    id          SERIAL PRIMARY KEY,
    edition     INTEGER NOT NULL CHECK (edition >= 1 AND edition <= 17),
    stage       VARCHAR(20) NOT NULL,
    title       VARCHAR(200) NOT NULL,
    original_category_label VARCHAR(50),
    exam_year   SMALLINT,
    pdf_file    VARCHAR(500),
    status      VARCHAR(20) DEFAULT 'draft',
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW(),
    UNIQUE(edition, stage)
);
CREATE INDEX idx_papers_edition ON papers(edition);
CREATE INDEX idx_papers_status ON papers(status);
""")

    lines.append("""
CREATE TABLE IF NOT EXISTS knowledge_points (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    slug        VARCHAR(100) UNIQUE NOT NULL,
    subject     VARCHAR(30) NOT NULL,
    parent_id   INTEGER REFERENCES knowledge_points(id),
    sort_order  SMALLINT DEFAULT 0
);
CREATE INDEX idx_kp_slug ON knowledge_points(slug);
""")

    lines.append("""
CREATE TABLE IF NOT EXISTS questions (
    id             SERIAL PRIMARY KEY,
    paper_id       INTEGER NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    question_no    VARCHAR(20) NOT NULL,
    sort_order     SMALLINT NOT NULL,
    question_type  VARCHAR(30) NOT NULL,
    score          DECIMAL(5,2),
    stem_md        TEXT NOT NULL,
    answer_md      TEXT,
    solution_md    TEXT NOT NULL,
    search_text    TEXT,
    source_page    SMALLINT,
    status         VARCHAR(20) DEFAULT 'draft',
    created_at     TIMESTAMP DEFAULT NOW(),
    updated_at     TIMESTAMP DEFAULT NOW(),
    UNIQUE(paper_id, question_no)
);
CREATE INDEX idx_questions_paper ON questions(paper_id, sort_order);
CREATE INDEX idx_questions_type ON questions(question_type);
CREATE INDEX idx_questions_status ON questions(status);
CREATE INDEX idx_questions_search ON questions(search_text);
""")

    lines.append("""
CREATE TABLE IF NOT EXISTS question_knowledge_points (
    question_id       INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    knowledge_point_id INTEGER NOT NULL REFERENCES knowledge_points(id) ON DELETE CASCADE,
    is_primary        BOOLEAN DEFAULT FALSE,
    PRIMARY KEY(question_id, knowledge_point_id)
);
CREATE UNIQUE INDEX idx_qkp_primary ON question_knowledge_points(question_id) WHERE is_primary = TRUE;
""")

    # 收藏和错题表（带 openid 字段，PG 用 RLS 控制用户隔离）
    lines.append("""
CREATE TABLE IF NOT EXISTS favorites (
    id          SERIAL PRIMARY KEY,
    openid      VARCHAR(128) NOT NULL,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    created_at  TIMESTAMP DEFAULT NOW(),
    UNIQUE(openid, question_id)
);
CREATE INDEX idx_favorites_openid ON favorites(openid);
""")

    lines.append("""
CREATE TABLE IF NOT EXISTS wrong_questions (
    id          SERIAL PRIMARY KEY,
    openid      VARCHAR(128) NOT NULL,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    created_at  TIMESTAMP DEFAULT NOW(),
    UNIQUE(openid, question_id)
);
CREATE INDEX idx_wq_openid ON wrong_questions(openid);
""")

    # ============ 插入知识体系 ============
    lines.append("\n-- ====== 知识体系 ======\n")
    kps = list(KnowledgePoint.objects.order_by("id"))
    for kp in kps:
        parent = str(kp.parent_id) if kp.parent_id else "NULL"
        lines.append(
            f"INSERT INTO knowledge_points (id, name, slug, subject, parent_id, sort_order) "
            f"VALUES ({kp.id}, '{escape(kp.name)}', '{escape(kp.slug)}', '{escape(kp.subject)}', {parent}, {kp.sort_order}) "
            f"ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;\n"
        )

    # ============ 插入试卷 ============
    lines.append("\n-- ====== 试卷 ======\n")
    papers = list(Paper.objects.order_by("edition", "stage"))
    paper_map = {}
    for p in papers:
        pdf = escape(p.pdf_file.name) if p.pdf_file else ""
        lines.append(
            f"INSERT INTO papers (id, edition, stage, title, original_category_label, exam_year, pdf_file, status) "
            f"VALUES ({p.id}, {p.edition}, '{escape(p.stage)}', '{escape(p.title)}', "
            f"'{escape(p.original_category_label)}', "
            f"{p.exam_year if p.exam_year else 'NULL'}, '{pdf}', '{escape(p.status)}') "
            f"ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;\n"
        )
        paper_map[p.id] = p.id

    # ============ 插入题目 ============
    lines.append("\n-- ====== 题目 ======\n")
    questions = list(Question.objects.select_related("paper").prefetch_related("knowledge_points").all())
    for q in questions:
        lines.append(
            f"INSERT INTO questions (id, paper_id, question_no, sort_order, question_type, score, "
            f"stem_md, answer_md, solution_md, search_text, source_page, status) "
            f"VALUES ({q.id}, {q.paper_id}, '{escape(q.question_no)}', {q.sort_order}, "
            f"'{escape(q.question_type)}', "
            f"{q.score if q.score is not None else 'NULL'}, "
            f"'{escape(q.stem_md)}', '{escape(q.answer_md or '')}', '{escape(q.solution_md)}', "
            f"'{escape(q.search_text)}', {q.source_page}, '{escape(q.status)}') "
            f"ON CONFLICT (id) DO UPDATE SET stem_md = EXCLUDED.stem_md;\n"
        )

        # ============ 题目-知识点关联 ============
        for qkp in q.questionknowledgepoint_set.select_related("knowledge_point"):
            lines.append(
                f"INSERT INTO question_knowledge_points (question_id, knowledge_point_id, is_primary) "
                f"VALUES ({q.id}, {qkp.knowledge_point_id}, {'TRUE' if qkp.is_primary else 'FALSE'}) "
                f"ON CONFLICT DO NOTHING;\n"
            )

    # 收集统计信息
    stats = {
        "papers": Paper.objects.count(),
        "questions": Question.objects.count(),
        "knowledge_points": KnowledgePoint.objects.count(),
        "question_knowledge_points": QuestionKnowledgePoint.objects.count(),
        "pdf_files": Paper.objects.filter(pdf_file__isnull=False).count(),
    }

    return "\n".join(lines), stats


if __name__ == "__main__":
    sql, stats = build_sql()

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    output_path = os.path.join(output_dir, "migrate_output.sql")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(sql)

    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print(f"\n✅ SQL 文件已生成: {output_path}")
    print(f"   共 {len(sql.splitlines())} 行，约 {len(sql) // 1024} KB")