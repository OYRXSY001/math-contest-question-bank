-- ====== 建表 ======


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


CREATE TABLE IF NOT EXISTS knowledge_points (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    slug        VARCHAR(100) UNIQUE NOT NULL,
    subject     VARCHAR(30) NOT NULL,
    parent_id   INTEGER REFERENCES knowledge_points(id),
    sort_order  SMALLINT DEFAULT 0
);
CREATE INDEX idx_kp_slug ON knowledge_points(slug);


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


CREATE TABLE IF NOT EXISTS question_knowledge_points (
    question_id       INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    knowledge_point_id INTEGER NOT NULL REFERENCES knowledge_points(id) ON DELETE CASCADE,
    is_primary        BOOLEAN DEFAULT FALSE,
    PRIMARY KEY(question_id, knowledge_point_id)
);
CREATE UNIQUE INDEX idx_qkp_primary ON question_knowledge_points(question_id) WHERE is_primary = TRUE;


CREATE TABLE IF NOT EXISTS favorites (
    id          SERIAL PRIMARY KEY,
    openid      VARCHAR(128) NOT NULL,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    created_at  TIMESTAMP DEFAULT NOW(),
    UNIQUE(openid, question_id)
);
CREATE INDEX idx_favorites_openid ON favorites(openid);


CREATE TABLE IF NOT EXISTS wrong_questions (
    id          SERIAL PRIMARY KEY,
    openid      VARCHAR(128) NOT NULL,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    created_at  TIMESTAMP DEFAULT NOW(),
    UNIQUE(openid, question_id)
);
CREATE INDEX idx_wq_openid ON wrong_questions(openid);


-- ====== 知识体系 ======
