# Question Bank Core Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enforce the approved question-publication gates, reject incomplete or unsafe workbook imports, and restore the PDF and sticky question-navigation UI.

**Architecture:** Keep the existing Django monolith and its model, management-command, Admin, and template boundaries. Add validation at the model and workbook-preflight layers, with no schema or dependency changes. Each task follows Django `TestCase` red-green-refactor cycles and lands as one focused commit.

**Tech Stack:** Python 3.12+, Django 5.2, SQLite, openpyxl, Django templates, Bootstrap 5, built-in Django test runner.

## Global Constraints

- Only include editions 1–17 and the non-mathematics A-category scope.
- Do not add mathematics-category, non-mathematics B-category, course, forum, ranking, payment, news, or automatic-grading features.
- Preserve each paper's original category label; use `non_math_a` as the fixed internal scope.
- Use only `preliminary` and `final` as stage values.
- Every published question must have non-empty detailed analysis, status `reviewed` or `published`, one primary knowledge point, a reviewer, a review timestamp, all three review flags, zero OCR issues, and zero KaTeX errors.
- Keep formulas as LaTeX inside Markdown; keep diagrams as image files.
- Public pages show only `published` papers and questions.
- Do not add Python or Node dependencies and do not create a database migration.
- Use built-in Django tests; do not add pytest.
- Tests for new or repaired behavior must fail for the expected reason before production changes; regression tests that preserve existing safe behavior may already pass.
- Work only on branch `non-math-a-question-bank`; do not merge to `main`.

## Final File Map

Only these tracked files change during implementation:

```text
question_bank/
├── admin.py
├── models.py
├── management/commands/import_question_bank.py
└── tests/
    ├── test_admin.py
    ├── test_import.py
    ├── test_models.py
    ├── test_queries.py
    └── test_views.py
templates/question_bank/paper_detail.html
```

---

### Task 1: Enforce complete publication review state

**Files:**

- Modify: `question_bank/models.py:168-179`
- Modify: `question_bank/admin.py:89-100`
- Modify: `question_bank/tests/test_models.py`
- Modify: `question_bank/tests/test_admin.py`
- Modify: `question_bank/tests/test_queries.py`
- Modify: `question_bank/tests/test_views.py`

**Interfaces:**

- Consumes: `Question.Status`, `QuestionKnowledgePoint`, `reviewed_by`, `reviewed_at`, and existing review counters.
- Produces: `Question.can_publish() -> bool`, returning true only for a saved, fully reviewed question with exactly one primary knowledge point.
- Preserves: `Question.clean()` blocks direct saves of invalid `published` questions; `QuestionAdmin.publish_reviewed()` publishes only eligible rows.

- [ ] **Step 1: Write failing model tests for the missing gates**

In `question_bank/tests/test_models.py`, import `django.utils.timezone`. Add a helper that creates a reviewed question without publishing it:

```python
def create_reviewed_question(self, **overrides):
    values = {
        "paper": self.paper,
        "question_no": "1",
        "sort_order": 1,
        "question_type": Question.Type.CALCULATION,
        "stem_md": r"求 \(x\) 的值。",
        "solution_md": "详细解析",
        "source_page": 1,
        "text_checked": True,
        "formula_checked": True,
        "solution_checked": True,
        "reviewed_by": self.user,
        "reviewed_at": timezone.now(),
        "status": Question.Status.REVIEWED,
    }
    values.update(overrides)
    return Question.objects.create(**values)
```

Add separate tests proving `can_publish()` returns false when the question has no primary knowledge point, no `reviewed_at`, or remains `draft`. Add a success test that creates one primary `QuestionKnowledgePoint`, changes status to `published`, saves, and verifies the rebuilt `search_text`.

- [ ] **Step 2: Run the model tests and verify RED**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_models --verbosity 2
```

Expected: the new missing-primary, missing-review-time, and draft-state assertions fail because the current `can_publish()` ignores those conditions.

- [ ] **Step 3: Implement the minimal model gate**

Update `Question.can_publish()` in `question_bank/models.py`:

```python
def can_publish(self):
    if self.pk is None:
        return False
    has_one_primary = (
        self.questionknowledgepoint_set.filter(is_primary=True).count() == 1
    )
    return all(
        (
            self.status in {self.Status.REVIEWED, self.Status.PUBLISHED},
            self.text_checked,
            self.formula_checked,
            self.solution_checked,
            self.reviewed_by_id is not None,
            self.reviewed_at is not None,
            self.unresolved_ocr_items == 0,
            self.katex_errors == 0,
            bool(self.solution_md.strip()),
            has_one_primary,
        )
    )
```

Do not add a migration. The existing conditional unique constraint continues to prevent two primary knowledge points.

Update `QuestionAdmin.publish_reviewed()` so a selected row is published only when its current status is `Question.Status.REVIEWED` and `question.can_publish()` is true:

```python
if question.status == Question.Status.REVIEWED and question.can_publish():
    question.status = Question.Status.PUBLISHED
    question.save(update_fields=["status", "search_text", "updated_at"])
    published += 1
else:
    skipped += 1
```

- [ ] **Step 4: Update existing published-question test fixtures**

Any test that currently creates `status="published"` before adding a primary knowledge point must use this sequence:

```python
question = Question.objects.create(
    # existing fields,
    reviewed_at=timezone.now(),
    status=Question.Status.REVIEWED,
)
QuestionKnowledgePoint.objects.create(
    question=question,
    knowledge_point=knowledge,
    is_primary=True,
)
question.status = Question.Status.PUBLISHED
question.save()
```

Apply the sequence to the published fixtures in `test_models.py`, `test_queries.py`, and `test_views.py`. Create a `KnowledgePoint` in `PublicPageTests.setUpTestData()` before publishing its shared question. Do not weaken assertions that unpublished content stays private.

- [ ] **Step 5: Add failing Admin action coverage**

In `question_bank/tests/test_admin.py`, add a test that sets all Boolean review fields and a reviewer but leaves `reviewed_at` or the primary knowledge point missing. Assert that `publish_reviewed()` leaves the question unpublished. Add a success test that supplies `reviewed_at`, status `reviewed`, and one primary knowledge point, then asserts the action changes status to `published`. Add a test proving an already published row is counted as skipped rather than published again.

- [ ] **Step 6: Run the Admin test and verify RED where applicable**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_admin --verbosity 2
```

Expected before the fixture and model updates are complete: the eligible-action test or missing-gate test fails against the old behavior. After Step 3 and the fixture changes, both cases pass without changing the Admin action's message contract.

- [ ] **Step 7: Run all affected test modules and verify GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_models question_bank.tests.test_admin question_bank.tests.test_queries question_bank.tests.test_views --verbosity 1
```

Expected: all affected tests pass.

- [ ] **Step 8: Commit Task 1**

```powershell
git add question_bank/models.py question_bank/admin.py question_bank/tests/test_models.py question_bank/tests/test_admin.py question_bank/tests/test_queries.py question_bank/tests/test_views.py
git commit -m "fix: enforce complete question review gates"
```

---

### Task 2: Reject empty workbooks and validate OCR evidence

**Files:**

- Modify: `question_bank/management/commands/import_question_bank.py`
- Modify: `question_bank/tests/test_import.py`

**Interfaces:**

- Consumes: workbook rows returned by `read_rows()`, `text_checked`, `unresolved_ocr_items`, and the existing `issues` aggregation.
- Produces: `as_ocr_confidence(value, label, issues) -> Decimal | None` and `validate_ocr_characters(row, label, issues) -> None`.
- Uses exact threshold: `MIN_OCR_CONFIDENCE = Decimal("0.90")`.

- [ ] **Step 1: Write failing empty-workbook tests**

Add two tests to `question_bank/tests/test_import.py`:

```python
def test_empty_inventory_is_rejected(self):
    inventory = self.root / "inventory.xlsx"
    questions = self.root / "questions.xlsx"
    self.write_workbook(inventory, INVENTORY_HEADERS, [])
    self.write_workbook(questions, QUESTION_HEADERS, self.valid_rows()[1])

    with self.assertRaisesMessage(CommandError, "inventory: 至少需要一行数据"):
        call_command(
            "import_question_bank",
            inventory=str(inventory),
            questions=str(questions),
            dry_run=True,
        )

def test_empty_questions_are_rejected(self):
    inventory_rows, _ = self.valid_rows()
    inventory = self.root / "inventory.xlsx"
    questions = self.root / "questions.xlsx"
    self.write_workbook(inventory, INVENTORY_HEADERS, inventory_rows)
    self.write_workbook(questions, QUESTION_HEADERS, [])

    with self.assertRaisesMessage(CommandError, "questions: 至少需要一行数据"):
        call_command(
            "import_question_bank",
            inventory=str(inventory),
            questions=str(questions),
            dry_run=True,
        )
```

- [ ] **Step 2: Run the empty-workbook tests and verify RED**

Run both tests by dotted name. Expected: the empty inventory case fails with downstream validation text and the empty questions case reports a successful zero-question dry-run instead of the required messages.

- [ ] **Step 3: Add the minimal empty-row preflight**

Immediately after `read_rows()` in `handle()`, initialize `issues` and append:

```python
if not paper_rows:
    issues.append("inventory: 至少需要一行数据")
if not question_rows:
    issues.append("questions: 至少需要一行数据")
```

Keep the existing validation calls so one run reports all detectable problems.

- [ ] **Step 4: Write failing OCR confidence and suspicious-character tests**

Add focused tests for these cases:

- `ocr_confidence` is blank.
- `ocr_confidence` is `-0.01` or `1.01`.
- `ocr_confidence=0.89`, `text_checked=False`, and `unresolved_ocr_items=0`.
- `ocr_confidence=0.89`, `text_checked=True`, and `unresolved_ocr_items=0` succeeds.
- `stem_md` contains `�`.
- `solution_md` contains `□`.

Each failure test must assert `CommandError`, the `questions 第2行` label, and the field-specific reason. Each case must assert the database stays empty.

- [ ] **Step 5: Run the OCR tests and verify RED**

Run the new tests by dotted name. Expected: current code accepts all six inputs or fails for an unrelated later reason, proving the missing preflight behavior.

- [ ] **Step 6: Implement OCR parsing and validation**

At module level:

```python
from decimal import Decimal, InvalidOperation

MIN_OCR_CONFIDENCE = Decimal("0.90")
SUSPICIOUS_OCR_CHARACTERS = {
    "�": "Unicode 替换字符",
    "□": "空方框",
}
```

Add:

```python
def as_ocr_confidence(value, label, issues):
    if value in (None, "") or isinstance(value, bool):
        issues.append(f"{label}: 必须是 0 到 1 之间的数字")
        return None
    try:
        confidence = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        issues.append(f"{label}: 必须是 0 到 1 之间的数字")
        return None
    if not confidence.is_finite() or not Decimal("0") <= confidence <= Decimal("1"):
        issues.append(f"{label}: 必须在 0 到 1 之间")
        return None
    return confidence


def validate_ocr_characters(row, label, issues):
    for field in ("stem_md", "answer_md", "solution_md"):
        text = str(row.get(field) or "")
        for character, name in SUSPICIOUS_OCR_CHARACTERS.items():
            if character in text:
                issues.append(f"{label} {field}: 包含{name} {character}")
```

In `validate_questions()`, parse `text_checked` once before the row update, parse `_ocr_confidence`, and apply:

```python
if (
    confidence is not None
    and confidence < MIN_OCR_CONFIDENCE
    and not text_checked
    and unresolved == 0
):
    issues.append(
        f"{label}: OCR 置信度低于 0.90 时必须登记 unresolved_ocr_items"
    )
validate_ocr_characters(row, label, issues)
```

Store `_ocr_confidence` in the normalized row for diagnostics; do not add a model field or migration.

- [ ] **Step 7: Run import tests and verify GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_import --verbosity 1
```

Expected: all existing and new import tests pass.

- [ ] **Step 8: Commit Task 2**

```powershell
git add question_bank/management/commands/import_question_bank.py question_bank/tests/test_import.py
git commit -m "fix: validate workbook OCR evidence"
```

---

### Task 3: Validate declared question images

**Files:**

- Modify: `question_bank/management/commands/import_question_bank.py`
- Modify: `question_bank/tests/test_import.py`

**Interfaces:**

- Consumes: comma-separated `image_files`, `settings.MEDIA_ROOT`, and the three Markdown content fields.
- Produces: `validate_question_image(root, relative, label, markdown_text, issues) -> None`.
- Uses exact limit: `MAX_IMAGE_BYTES = 10 * 1024 * 1024`.
- Accepts only: `.png`, `.jpg`, `.jpeg`, `.webp` with matching file signatures.

- [ ] **Step 1: Add a helper for valid test image data**

In `test_import.py`, add:

```python
def write_valid_png(self, relative="questions/q1.png"):
    path = self.media / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG\r\n\x1a\nvalid-test-image")
    return relative
```

- [ ] **Step 2: Write failing image-validation tests**

Add separate tests that declare an image and prove import fails when:

- the relative path escapes `MEDIA_ROOT`;
- the extension is `.svg`;
- a `.png` file has a non-PNG header;
- the file exceeds 10 MiB;
- a valid image exists but its relative path does not occur in `stem_md`, `answer_md`, or `solution_md`.

Add a success test that puts the value from `write_valid_png()` into `image_files` and appends `![题图](questions/q1.png)` to `stem_md`. Run the command with `dry_run=True` and assert that no `CommandError` is raised.

- [ ] **Step 3: Run the new image tests and verify RED**

Run the six new tests by dotted name. Expected: the existing path-escape test may already pass; extension, header, size, reference, and legal-image behavior expose the missing validation. If a test passes against existing code, confirm it exercises the existing path-safety behavior and keep it as regression coverage.

- [ ] **Step 4: Implement focused image validation**

Add constants:

```python
MAX_IMAGE_BYTES = 10 * 1024 * 1024
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
```

Add helpers:

```python
def image_signature_matches(path):
    with path.open("rb") as source:
        header = source.read(12)
    suffix = path.suffix.lower()
    if suffix == ".png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    if suffix in {".jpg", ".jpeg"}:
        return header.startswith(b"\xff\xd8\xff")
    if suffix == ".webp":
        return header.startswith(b"RIFF") and header[8:12] == b"WEBP"
    return False
```

Implement `validate_question_image()` by resolving the path under `MEDIA_ROOT`, rejecting path escape and missing files, then checking suffix, size, signature, and exact occurrence of `relative` in the combined Markdown text. Read only the first 12 bytes in production code rather than loading the full image into memory.

Replace the current generic `safe_file()` call for `image_files` with `validate_question_image()`. Keep `safe_file()` for PDFs and private source crops.

- [ ] **Step 5: Run the complete import test module and verify GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_import --verbosity 1
```

Expected: all import tests pass, including the legal PNG dry-run.

- [ ] **Step 6: Commit Task 3**

```powershell
git add question_bank/management/commands/import_question_bank.py question_bank/tests/test_import.py
git commit -m "fix: validate imported question images"
```

---

### Task 4: Restore PDF and sticky question navigation UI

**Files:**

- Modify: `templates/question_bank/paper_detail.html`
- Modify: `question_bank/tests/test_views.py`

**Interfaces:**

- Consumes: existing `paper-download` route, `paper.pdf_file`, and `.question-number-nav` CSS.
- Produces: a conditional “下载 PDF” link and sticky, horizontally scrollable question navigation.

- [ ] **Step 1: Write failing page tests**

In `PublicPageTests`, add or replace tests with:

```python
def test_paper_detail_hides_download_when_pdf_is_missing(self):
    response = self.client.get(reverse("paper-detail", args=[self.paper.pk]))

    self.assertNotContains(response, reverse("paper-download", args=[self.paper.pk]))

def test_paper_detail_links_to_download_when_pdf_exists(self):
    upload = SimpleUploadedFile(
        "paper.pdf", b"%PDF-1.4\n%%EOF\n", content_type="application/pdf"
    )
    self.paper.pdf_file.save(upload.name, upload, save=True)
    self.addCleanup(self.paper.pdf_file.delete, save=False)

    response = self.client.get(reverse("paper-detail", args=[self.paper.pk]))

    self.assertContains(response, reverse("paper-download", args=[self.paper.pk]))
    self.assertContains(response, "下载 PDF")

def test_paper_detail_uses_sticky_question_navigation(self):
    response = self.client.get(reverse("paper-detail", args=[self.paper.pk]))

    self.assertContains(response, 'class="question-number-nav')
```

- [ ] **Step 2: Run the new page tests and verify RED**

Run the three tests by dotted name. Expected: the missing-PDF test passes; the PDF-link and sticky-class tests fail against the current template.

- [ ] **Step 3: Implement the minimal template change**

Replace the title line in `paper_detail.html` with:

```django
<div class="d-flex flex-wrap justify-content-between gap-3">
  <h1 class="h2">{{ paper.title }}</h1>
  {% if paper.pdf_file %}
    <a class="btn btn-outline-primary" href="{% url 'paper-download' paper.pk %}">下载 PDF</a>
  {% endif %}
</div>
```

Change the question navigation opening tag to:

```django
<nav class="question-number-nav d-flex gap-2 overflow-x-auto mb-3" aria-label="题号导航">
```

Do not alter the card layout, question loop, or CSS.

- [ ] **Step 4: Run page tests and verify GREEN**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_views --verbosity 1
```

Expected: all page and user-list tests pass.

- [ ] **Step 5: Commit Task 4**

```powershell
git add templates/question_bank/paper_detail.html question_bank/tests/test_views.py
git commit -m "fix: restore paper detail actions"
```

---

## Final Verification

After all four task reviews pass, run from the worktree root:

```powershell
.\.venv\Scripts\python.exe manage.py test --verbosity 1
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
git diff --check main...HEAD
git status --short --branch
```

Expected:

- The full test suite passes with no failures.
- Django reports no system-check issues.
- Django reports `No changes detected`.
- Git reports no whitespace errors and no uncommitted tracked changes.
