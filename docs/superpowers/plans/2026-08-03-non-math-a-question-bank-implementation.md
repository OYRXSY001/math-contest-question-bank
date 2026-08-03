# 非数学 A 类真题网站 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deployable Django website for viewing, filtering, searching, downloading, collecting, and reviewing the 1st–17th National College Student Mathematics Competition non-mathematics A-category preliminary and final papers.

**Architecture:** Use one Django 5.2 project with server-rendered templates, SQLite, Django Auth, and Django Admin. Store questions as Markdown plus LaTeX, render formulas in the browser with locally installed KaTeX, and import reviewed workbooks through an atomic Django management command.

**Tech Stack:** Python 3.13, Django 5.2 LTS, SQLite, Django Template, Bootstrap 5, KaTeX, Python-Markdown, openpyxl, Gunicorn, Caddy.

## Global Constraints

- Only include editions 1–17 and the non-mathematics A-category scope.
- Do not add mathematics-category, non-mathematics B-category, course, forum, ranking, payment, news, or automatic-grading features.
- Preserve each paper's original category label; use `non_math_a` as the fixed internal scope.
- Use only `preliminary` and `final` as stage values.
- Every published question must have non-empty detailed analysis and pass text, formula, solution, OCR, and KaTeX review gates.
- Keep formulas as LaTeX inside Markdown; keep diagrams as image files.
- Public pages show only `published` papers and questions.
- Use SQLite substring search for the first release; do not add Redis or a separate search service.
- Support Windows local development and a single low-cost Linux server deployment.
- Use built-in Django tests; do not add pytest.

---

## Final File Map

```text
.
├── .env.example
├── .gitignore
├── manage.py
├── package.json
├── requirements.txt
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── question_bank/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── katex.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── models.py
│   ├── queries.py
│   ├── taxonomy.py
│   ├── urls.py
│   ├── views.py
│   ├── management/
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── import_question_bank.py
│   │       └── seed_knowledge_points.py
│   ├── templatetags/
│   │   ├── __init__.py
│   │   └── content.py
│   └── tests/
│       ├── __init__.py
│       ├── test_admin.py
│       ├── test_download.py
│       ├── test_import.py
│       ├── test_models.py
│       ├── test_queries.py
│       └── test_views.py
├── scripts/
│   └── validate-katex.mjs
├── static/
│   ├── css/site.css
│   └── js/math.js
├── templates/
│   ├── 404.html
│   ├── base.html
│   ├── home.html
│   ├── account/register.html
│   ├── registration/login.html
│   └── question_bank/
│       ├── _filters.html
│       ├── _question_card.html
│       ├── favorites.html
│       ├── paper_detail.html
│       ├── paper_list.html
│       ├── question_detail.html
│       └── wrong_questions.html
├── data/
│   ├── import/.gitkeep
│   └── review/.gitkeep
├── media/.gitkeep
└── deploy/
    ├── Caddyfile
    ├── backup.sh
    ├── cmc-a-backup.cron
    └── cmc-a.service
```

## Task 1: Bootstrap Django and the custom user model

**Files:**

- Create: `.gitignore`
- Create: `.env.example`
- Create: `requirements.txt`
- Create: `package.json`
- Create: `manage.py`
- Create: `config/settings.py`
- Create: `config/urls.py`
- Create: `config/asgi.py`
- Create: `config/wsgi.py`
- Create: `accounts/apps.py`
- Create: `accounts/models.py`
- Create: `accounts/admin.py`
- Create: `accounts/tests.py`
- Create: `question_bank/apps.py`
- Create: package `__init__.py` and migration `__init__.py` files shown in the file map

**Interfaces:**

- Produces: `accounts.User`, configured through `AUTH_USER_MODEL = "accounts.User"`.
- Produces: a runnable Django project at `config.settings`.

- [ ] **Step 1: Initialize Git and create the Python environment**

Run:

```powershell
git init
py -3.13 -m venv .venv
```

Expected: Git creates `.git`, and `.venv\Scripts\python.exe` exists.

- [ ] **Step 2: Add dependency and ignore files**

Create `requirements.txt`:

```text
Django>=5.2,<5.3
Markdown>=3.8,<4
openpyxl>=3.1,<4
gunicorn>=23,<24
```

Create `package.json`:

```json
{
  "name": "cmc-non-math-a-question-bank",
  "private": true,
  "dependencies": {
    "bootstrap": "5.3.8",
    "katex": "0.18.1"
  }
}
```

Create `.gitignore`:

```gitignore
.venv/
__pycache__/
*.py[cod]
.env
db.sqlite3
node_modules/
staticfiles/
media/*
!media/.gitkeep
data/import/*
!data/import/.gitkeep
data/review/*
!data/review/.gitkeep
*.log
```

Create `.env.example`:

```dotenv
DJANGO_DEBUG=1
DJANGO_SECRET_KEY=dev-only-key
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

- [ ] **Step 3: Install dependencies and generate the Django skeleton**

Run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\django-admin.exe startproject config .
.\.venv\Scripts\python.exe manage.py startapp accounts
.\.venv\Scripts\python.exe manage.py startapp question_bank
npm.cmd install
New-Item -ItemType Directory -Force -Path templates,static/css,static/js,data/import,data/review,media
New-Item -ItemType File -Force -Path data/import/.gitkeep,data/review/.gitkeep,media/.gitkeep
```

Expected: Django creates `manage.py`, `config/`, `accounts/`, and `question_bank/`; npm creates `node_modules/`.

- [ ] **Step 4: Configure Django**

Replace `config/settings.py` with:

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-key")
if not DEBUG and SECRET_KEY == "dev-only-key":
    raise RuntimeError("DJANGO_SECRET_KEY must be set when DEBUG=0")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "question_bank",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
REVIEW_ROOT = BASE_DIR / "data" / "review"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```

Replace `config/urls.py` with:

```python
from django.contrib import admin
from django.urls import path

urlpatterns = [path("admin/", admin.site.urls)]
```

- [ ] **Step 5: Create the custom user model and its failing test**

Replace `accounts/models.py` with:

```python
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass
```

Replace `accounts/admin.py` with:

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

admin.site.register(User, UserAdmin)
```

Replace `accounts/tests.py` with:

```python
from django.contrib.auth import get_user_model
from django.test import TestCase


class UserModelTests(TestCase):
    def test_project_uses_custom_user_model(self):
        user = get_user_model().objects.create_user("alice", password="safe-pass-123")

        self.assertEqual(user._meta.label, "accounts.User")
        self.assertTrue(user.check_password("safe-pass-123"))
```

- [ ] **Step 6: Create migrations and run the test**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations accounts
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py test accounts
.\.venv\Scripts\python.exe manage.py check
```

Expected: one test passes and `System check identified no issues`.

- [ ] **Step 7: Commit the bootstrap**

```powershell
git add .gitignore .env.example requirements.txt package.json package-lock.json manage.py config accounts question_bank data media static
git commit -m "chore: bootstrap Django question bank"
```

## Task 2: Implement papers, questions, knowledge, favorites, and wrong-question models

**Files:**

- Create: `question_bank/models.py`
- Create: `question_bank/tests/__init__.py`
- Create: `question_bank/tests/test_models.py`
- Create: generated `question_bank/migrations/0001_initial.py`

**Interfaces:**

- Consumes: `settings.AUTH_USER_MODEL` from Task 1.
- Produces: `Paper`, `Question`, `KnowledgePoint`, `QuestionKnowledgePoint`, `Favorite`, `WrongQuestion`.
- Produces: `Question.can_publish() -> bool` and automatic `Question.search_text` normalization.

- [ ] **Step 1: Write model tests that fail because the models do not exist**

Create `question_bank/tests/__init__.py` as an empty file.

Create `question_bank/tests/test_models.py`:

```python
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from question_bank.models import (
    Favorite,
    KnowledgePoint,
    Paper,
    Question,
    QuestionKnowledgePoint,
    WrongQuestion,
)


class QuestionBankModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user("reviewer", password="pass-12345")
        cls.paper = Paper.objects.create(
            edition=17,
            stage=Paper.Stage.PRELIMINARY,
            original_category_label="非数学A类",
            title="第17届非数学A类初赛",
        )
        cls.knowledge = KnowledgePoint.objects.create(
            name="函数极限", slug="function-limit", subject=KnowledgePoint.Subject.CALCULUS
        )

    def test_edition_must_be_between_1_and_17(self):
        paper = Paper(
            edition=18,
            stage=Paper.Stage.FINAL,
            original_category_label="非数学A类",
            title="非法试卷",
        )

        with self.assertRaises(ValidationError):
            paper.full_clean()

    def test_scope_category_cannot_change(self):
        paper = Paper(
            edition=1,
            stage=Paper.Stage.PRELIMINARY,
            scope_category="non_math_b",
            original_category_label="非数学类",
            title="非法类别",
        )

        with self.assertRaises(ValidationError):
            paper.full_clean()

    def test_unreviewed_question_cannot_be_published(self):
        question = Question(
            paper=self.paper,
            question_no="1",
            sort_order=1,
            question_type=Question.Type.CALCULATION,
            stem_md=r"求 \(x\) 的值。",
            solution_md="详细解析",
            source_page=1,
            status=Question.Status.PUBLISHED,
        )

        with self.assertRaises(ValidationError):
            question.save()

    def test_reviewed_question_can_be_published_and_builds_search_text(self):
        question = Question.objects.create(
            paper=self.paper,
            question_no="1",
            sort_order=1,
            question_type=Question.Type.CALCULATION,
            stem_md=r"计算函数极限 \(\lim_{x\to0}x\)。",
            answer_md="0",
            solution_md="利用极限定义可得 0。",
            source_page=1,
            text_checked=True,
            formula_checked=True,
            solution_checked=True,
            reviewed_by=self.user,
            status=Question.Status.PUBLISHED,
        )

        self.assertTrue(question.can_publish())
        self.assertIn("函数极限", question.search_text)
        self.assertIn("第17届非数学A类初赛", question.search_text)

    def test_only_one_primary_knowledge_point_is_allowed(self):
        question = Question.objects.create(
            paper=self.paper,
            question_no="2",
            sort_order=2,
            question_type=Question.Type.PROOF,
            stem_md="证明题",
            solution_md="证明过程",
            source_page=1,
        )
        other = KnowledgePoint.objects.create(
            name="函数连续", slug="function-continuity", subject=KnowledgePoint.Subject.CALCULUS
        )
        QuestionKnowledgePoint.objects.create(
            question=question, knowledge_point=self.knowledge, is_primary=True
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            QuestionKnowledgePoint.objects.create(
                question=question, knowledge_point=other, is_primary=True
            )

    def test_favorite_and_wrong_question_are_unique_per_user(self):
        question = Question.objects.create(
            paper=self.paper,
            question_no="3",
            sort_order=3,
            question_type=Question.Type.FILL_BLANK,
            stem_md="填空题",
            solution_md="解析",
            source_page=1,
        )
        Favorite.objects.create(user=self.user, question=question)
        WrongQuestion.objects.create(user=self.user, question=question)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Favorite.objects.create(user=self.user, question=question)
        with self.assertRaises(IntegrityError), transaction.atomic():
            WrongQuestion.objects.create(user=self.user, question=question)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_models
```

Expected: FAIL with `ImportError` because the six models are not defined.

- [ ] **Step 3: Implement the models and constraints**

Replace `question_bank/models.py` with:

```python
import re
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


MAX_PDF_BYTES = 50 * 1024 * 1024


def validate_pdf(upload):
    if upload.size > MAX_PDF_BYTES:
        raise ValidationError("PDF 不能超过 50 MB。")
    position = upload.tell()
    header = upload.read(5)
    upload.seek(position)
    if header != b"%PDF-":
        raise ValidationError("上传文件不是有效 PDF。")


def paper_pdf_path(instance, filename):
    return f"papers/edition-{instance.edition:02d}/{instance.stage}.pdf"


def normalize_search_text(*parts):
    text = " ".join(part or "" for part in parts)
    text = re.sub(r"\\[A-Za-z]+|[\\{}$^_]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


class Paper(models.Model):
    class Stage(models.TextChoices):
        PRELIMINARY = "preliminary", "初赛"
        FINAL = "final", "决赛"

    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        REVIEWED = "reviewed", "已复核"
        PUBLISHED = "published", "已发布"

    edition = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(17)]
    )
    stage = models.CharField(max_length=20, choices=Stage.choices)
    scope_category = models.CharField(
        max_length=20, default="non_math_a", editable=False
    )
    original_category_label = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    exam_year = models.PositiveSmallIntegerField(blank=True, null=True)
    pdf_file = models.FileField(
        upload_to=paper_pdf_path, validators=[validate_pdf], blank=True
    )
    source_url = models.URLField(max_length=1000, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-edition", "-stage"]
        constraints = [
            models.CheckConstraint(
                condition=Q(edition__gte=1, edition__lte=17),
                name="paper_edition_1_to_17",
            ),
            models.CheckConstraint(
                condition=Q(scope_category="non_math_a"),
                name="paper_scope_non_math_a",
            ),
            models.CheckConstraint(
                condition=Q(stage__in=["preliminary", "final"]),
                name="paper_stage_preliminary_or_final",
            ),
            models.UniqueConstraint(
                fields=["edition", "stage"], name="unique_paper_edition_stage"
            ),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class KnowledgePoint(models.Model):
    class Subject(models.TextChoices):
        CALCULUS = "calculus", "高等数学"
        FINAL_LINEAR_ALGEBRA = "final_linear_algebra", "决赛·线性代数"

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    subject = models.CharField(max_length=30, choices=Subject.choices)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="children", blank=True, null=True
    )
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["subject", "sort_order", "name"]

    def __str__(self):
        return self.name


class Question(models.Model):
    class Type(models.TextChoices):
        FILL_BLANK = "fill_blank", "填空题"
        CALCULATION = "calculation", "计算题"
        PROOF = "proof", "证明题"
        COMPREHENSIVE = "comprehensive", "综合题"

    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        REVIEWED = "reviewed", "已复核"
        PUBLISHED = "published", "已发布"

    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name="questions")
    question_no = models.CharField(max_length=20)
    sort_order = models.PositiveSmallIntegerField()
    question_type = models.CharField(max_length=30, choices=Type.choices)
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    stem_md = models.TextField()
    answer_md = models.TextField(blank=True)
    solution_md = models.TextField()
    search_text = models.TextField(blank=True, editable=False)
    source_page = models.PositiveSmallIntegerField()
    source_crop = models.CharField(max_length=500, blank=True)
    text_checked = models.BooleanField(default=False)
    formula_checked = models.BooleanField(default=False)
    solution_checked = models.BooleanField(default=False)
    unresolved_ocr_items = models.PositiveSmallIntegerField(default=0)
    katex_errors = models.PositiveSmallIntegerField(default=0)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reviewed_questions",
        blank=True,
        null=True,
    )
    reviewed_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    knowledge_points = models.ManyToManyField(
        KnowledgePoint, through="QuestionKnowledgePoint", related_name="questions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["paper", "sort_order"]
        constraints = [
            models.UniqueConstraint(
                fields=["paper", "question_no"], name="unique_question_number_per_paper"
            )
        ]
        indexes = [
            models.Index(fields=["status", "question_type"]),
            models.Index(fields=["paper", "sort_order"]),
        ]

    def can_publish(self):
        return all(
            (
                self.text_checked,
                self.formula_checked,
                self.solution_checked,
                self.reviewed_by_id is not None,
                self.unresolved_ocr_items == 0,
                self.katex_errors == 0,
                bool(self.solution_md.strip()),
            )
        )

    def clean(self):
        if self.status == self.Status.PUBLISHED and not self.can_publish():
            raise ValidationError("题目未通过全部发布检查。")

    def save(self, *args, **kwargs):
        self.search_text = normalize_search_text(
            self.paper.title, self.stem_md, self.answer_md, self.solution_md
        )
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.paper.title} 第{self.question_no}题"


class QuestionKnowledgePoint(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    knowledge_point = models.ForeignKey(KnowledgePoint, on_delete=models.PROTECT)
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["question", "knowledge_point"],
                name="unique_question_knowledge_point",
            ),
            models.UniqueConstraint(
                fields=["question"],
                condition=Q(is_primary=True),
                name="one_primary_knowledge_per_question",
            ),
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites"
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "question"], name="unique_user_favorite"
            )
        ]


class WrongQuestion(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wrong_questions"
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="marked_wrong_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "question"], name="unique_user_wrong_question"
            )
        ]
```

- [ ] **Step 4: Generate migrations and rerun model tests**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations question_bank
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_models
```

Expected: six model tests pass.

- [ ] **Step 5: Commit the data model**

```powershell
git add question_bank/models.py question_bank/migrations question_bank/tests
git commit -m "feat: add question bank data model"
```

## Task 3: Seed the fixed knowledge taxonomy and add the basic admin

**Files:**

- Create: `question_bank/taxonomy.py`
- Create: `question_bank/management/__init__.py`
- Create: `question_bank/management/commands/__init__.py`
- Create: `question_bank/management/commands/seed_knowledge_points.py`
- Modify: `question_bank/admin.py`
- Create: `question_bank/tests/test_admin.py`

**Interfaces:**

- Consumes: `KnowledgePoint` and all content models from Task 2.
- Produces: `seed_knowledge_points` idempotent command.
- Produces: Django Admin list, search, and filters for all content models.

- [ ] **Step 1: Write a failing taxonomy command test**

Create `question_bank/tests/test_admin.py`:

```python
from django.core.management import call_command
from django.test import TestCase

from question_bank.models import KnowledgePoint


class KnowledgeSeedTests(TestCase):
    def test_seed_command_is_idempotent_and_contains_only_allowed_subjects(self):
        call_command("seed_knowledge_points")
        first_count = KnowledgePoint.objects.count()
        call_command("seed_knowledge_points")

        self.assertGreater(first_count, 30)
        self.assertEqual(KnowledgePoint.objects.count(), first_count)
        self.assertSetEqual(
            set(KnowledgePoint.objects.values_list("subject", flat=True)),
            {"calculus", "final_linear_algebra"},
        )
        self.assertTrue(KnowledgePoint.objects.filter(slug="function-limit").exists())
        self.assertTrue(KnowledgePoint.objects.filter(slug="eigenvalue").exists())
```

- [ ] **Step 2: Run the test to verify the command is missing**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_admin.KnowledgeSeedTests
```

Expected: FAIL with `Unknown command: 'seed_knowledge_points'`.

- [ ] **Step 3: Define the fixed taxonomy**

Create `question_bank/taxonomy.py`:

```python
TAXONOMY = (
    ("calculus", "函数、极限与连续", "limits-continuity", (
        ("函数性质", "function-properties"),
        ("数列极限", "sequence-limit"),
        ("函数极限", "function-limit"),
        ("无穷小与无穷大", "infinitesimal-infinite"),
        ("连续与间断点", "continuity-discontinuity"),
    )),
    ("calculus", "一元函数微分学", "single-variable-differential", (
        ("导数与微分", "derivative-differential"),
        ("中值定理", "mean-value-theorem"),
        ("Taylor公式", "taylor-formula"),
        ("单调性与极值", "monotonicity-extrema"),
        ("凹凸性与拐点", "concavity-inflection"),
        ("渐近线", "asymptote"),
    )),
    ("calculus", "一元函数积分学", "single-variable-integral", (
        ("不定积分", "indefinite-integral"),
        ("定积分", "definite-integral"),
        ("定积分应用", "definite-integral-application"),
        ("反常积分", "improper-integral"),
        ("含参积分", "parameter-integral"),
    )),
    ("calculus", "多元函数微分学", "multivariable-differential", (
        ("多元函数极限与连续", "multivariable-limit-continuity"),
        ("偏导数与全微分", "partial-total-differential"),
        ("复合函数与隐函数", "composite-implicit-function"),
        ("方向导数与梯度", "directional-derivative-gradient"),
        ("多元函数极值", "multivariable-extrema"),
        ("Lagrange乘数法", "lagrange-multiplier"),
    )),
    ("calculus", "重积分", "multiple-integral", (
        ("二重积分", "double-integral"),
        ("三重积分", "triple-integral"),
        ("坐标变换", "coordinate-transform"),
    )),
    ("calculus", "曲线积分与曲面积分", "line-surface-integral", (
        ("第一、第二类曲线积分", "line-integral"),
        ("第一、第二类曲面积分", "surface-integral"),
        ("Green公式", "green-formula"),
        ("Gauss公式", "gauss-formula"),
        ("Stokes公式", "stokes-formula"),
    )),
    ("calculus", "无穷级数", "infinite-series", (
        ("数项级数", "number-series"),
        ("幂级数", "power-series"),
        ("Fourier级数", "fourier-series"),
    )),
    ("calculus", "常微分方程", "ordinary-differential-equation", (
        ("一阶微分方程", "first-order-ode"),
        ("高阶微分方程", "higher-order-ode"),
        ("微分方程综合应用", "ode-application"),
    )),
    ("calculus", "空间解析几何", "spatial-analytic-geometry", (
        ("向量与坐标", "vector-coordinate"),
        ("空间平面与直线", "plane-line"),
        ("曲面与曲线", "surface-curve"),
    )),
    ("final_linear_algebra", "决赛·线性代数", "final-linear-algebra", (
        ("行列式与矩阵", "determinant-matrix"),
        ("线性方程组", "linear-equation-system"),
        ("向量组", "vector-group"),
        ("特征值与特征向量", "eigenvalue"),
        ("二次型", "quadratic-form"),
    )),
)
```

- [ ] **Step 4: Implement the idempotent seed command**

Create empty `question_bank/management/__init__.py` and `question_bank/management/commands/__init__.py`.

Create `question_bank/management/commands/seed_knowledge_points.py`:

```python
from django.core.management.base import BaseCommand

from question_bank.models import KnowledgePoint
from question_bank.taxonomy import TAXONOMY


class Command(BaseCommand):
    help = "Create or update the fixed non-mathematics A knowledge taxonomy."

    def handle(self, *args, **options):
        count = 0
        for group_order, (subject, group_name, group_slug, children) in enumerate(TAXONOMY):
            parent, _ = KnowledgePoint.objects.update_or_create(
                slug=group_slug,
                defaults={
                    "name": group_name,
                    "subject": subject,
                    "parent": None,
                    "sort_order": group_order,
                },
            )
            count += 1
            for child_order, (name, slug) in enumerate(children):
                KnowledgePoint.objects.update_or_create(
                    slug=slug,
                    defaults={
                        "name": name,
                        "subject": subject,
                        "parent": parent,
                        "sort_order": child_order,
                    },
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded {count} knowledge points."))
```

- [ ] **Step 5: Register the content models in Django Admin**

Replace `question_bank/admin.py` with:

```python
from django.contrib import admin

from .models import (
    Favorite,
    KnowledgePoint,
    Paper,
    Question,
    QuestionKnowledgePoint,
    WrongQuestion,
)


class QuestionKnowledgeInline(admin.TabularInline):
    model = QuestionKnowledgePoint
    extra = 0


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ("edition", "stage", "original_category_label", "status")
    list_filter = ("edition", "stage", "status")
    search_fields = ("title", "original_category_label")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("paper", "question_no", "question_type", "status")
    list_filter = ("paper__edition", "paper__stage", "question_type", "status")
    search_fields = ("stem_md", "answer_md", "solution_md")
    inlines = (QuestionKnowledgeInline,)


@admin.register(KnowledgePoint)
class KnowledgePointAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "parent", "sort_order")
    list_filter = ("subject",)
    search_fields = ("name", "slug")


admin.site.register(Favorite)
admin.site.register(WrongQuestion)
```

- [ ] **Step 6: Run the taxonomy and admin checks**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_admin.KnowledgeSeedTests
.\.venv\Scripts\python.exe manage.py seed_knowledge_points
.\.venv\Scripts\python.exe manage.py check
```

Expected: the test passes, the command reports the seeded count, and Django reports no issues.

- [ ] **Step 7: Commit taxonomy and admin**

```powershell
git add question_bank/admin.py question_bank/taxonomy.py question_bank/management question_bank/tests/test_admin.py
git commit -m "feat: add fixed knowledge taxonomy and admin"
```

## Task 4: Implement reusable filtering and keyword search

**Files:**

- Create: `question_bank/forms.py`
- Create: `question_bank/queries.py`
- Create: `question_bank/tests/test_queries.py`

**Interfaces:**

- Consumes: `Question`, `KnowledgePoint`, `Favorite`, and `WrongQuestion`.
- Produces: `filtered_questions(params, base_queryset=None) -> tuple[QuerySet, QuestionFilterForm]`.
- Produces: `with_user_flags(queryset, user) -> QuerySet` with Boolean `is_favorite` and `is_wrong` annotations.

- [ ] **Step 1: Write failing query tests**

Create `question_bank/tests/test_queries.py`:

```python
from django.contrib.auth import get_user_model
from django.http import QueryDict
from django.test import TestCase

from question_bank.models import KnowledgePoint, Paper, Question, QuestionKnowledgePoint
from question_bank.queries import filtered_questions


class QuestionQueryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.reviewer = get_user_model().objects.create_user("query-reviewer")
        cls.limit = KnowledgePoint.objects.create(
            name="函数极限", slug="function-limit", subject="calculus"
        )
        cls.continuity = KnowledgePoint.objects.create(
            name="连续与间断点", slug="continuity-discontinuity", subject="calculus"
        )
        cls.preliminary = Paper.objects.create(
            edition=17,
            stage="preliminary",
            original_category_label="非数学A类",
            title="第17届非数学A类初赛",
            status="published",
        )
        cls.final = Paper.objects.create(
            edition=16,
            stage="final",
            original_category_label="非数学A类",
            title="第16届非数学A类决赛",
            status="published",
        )
        cls.q_limit = cls.create_question(
            cls.preliminary, "1", "proof", "证明函数极限存在", cls.limit
        )
        cls.q_continuity = cls.create_question(
            cls.preliminary, "2", "calculation", "判断连续性", cls.continuity
        )
        cls.q_final = cls.create_question(
            cls.final, "1", "proof", "决赛极限证明", cls.limit
        )
        Question.objects.create(
            paper=cls.preliminary,
            question_no="3",
            sort_order=3,
            question_type="proof",
            stem_md="未发布题目",
            solution_md="解析",
            source_page=1,
        )

    @classmethod
    def create_question(cls, paper, number, question_type, stem, knowledge):
        question = Question.objects.create(
            paper=paper,
            question_no=number,
            sort_order=int(number),
            question_type=question_type,
            stem_md=stem,
            answer_md="答案关键词",
            solution_md="详细解析关键词",
            source_page=1,
            text_checked=True,
            formula_checked=True,
            solution_checked=True,
            reviewed_by=cls.reviewer,
            status="published",
        )
        QuestionKnowledgePoint.objects.create(
            question=question, knowledge_point=knowledge, is_primary=True
        )
        return question

    def test_same_dimension_is_or(self):
        params = QueryDict(mutable=True)
        params.setlist("knowledge", ["function-limit", "continuity-discontinuity"])

        questions, form = filtered_questions(params)

        self.assertTrue(form.is_valid())
        self.assertSetEqual(
            set(questions.values_list("id", flat=True)),
            {self.q_limit.id, self.q_continuity.id, self.q_final.id},
        )

    def test_different_dimensions_are_and(self):
        params = QueryDict(
            "edition=17&stage=preliminary&question_type=proof&knowledge=function-limit"
        )

        questions, _ = filtered_questions(params)

        self.assertEqual(list(questions), [self.q_limit])

    def test_keyword_searches_question_content(self):
        questions, _ = filtered_questions(QueryDict("q=详细解析关键词&edition=16"))

        self.assertEqual(list(questions), [self.q_final])

    def test_invalid_filter_returns_no_results(self):
        questions, form = filtered_questions(QueryDict("edition=18"))

        self.assertFalse(form.is_valid())
        self.assertFalse(questions.exists())

    def test_unpublished_questions_are_always_excluded(self):
        questions, _ = filtered_questions(QueryDict())

        self.assertEqual(questions.count(), 3)
```

- [ ] **Step 2: Run the query tests to verify they fail**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_queries
```

Expected: FAIL with `ModuleNotFoundError: No module named 'question_bank.queries'`.

- [ ] **Step 3: Implement the validated filter form**

Create `question_bank/forms.py`:

```python
from django import forms

from .models import KnowledgePoint, Paper, Question


class QuestionFilterForm(forms.Form):
    edition = forms.TypedChoiceField(
        required=False,
        coerce=int,
        empty_value=None,
        choices=[("", "全部届数")] + [(number, f"第{number}届") for number in range(1, 18)],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    stage = forms.ChoiceField(
        required=False,
        choices=[("", "全部阶段"), *Paper.Stage.choices],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    question_type = forms.ChoiceField(
        required=False,
        choices=[("", "全部题型"), *Question.Type.choices],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    knowledge = forms.MultipleChoiceField(
        required=False,
        choices=(),
        widget=forms.CheckboxSelectMultiple,
    )
    q = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.SearchInput(
            attrs={"class": "form-control", "placeholder": "输入题干或解析关键词"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["knowledge"].choices = list(
            KnowledgePoint.objects.filter(parent__isnull=False).values_list("slug", "name")
        )
```

- [ ] **Step 4: Implement the shared query functions**

Create `question_bank/queries.py`:

```python
from django.db.models import Exists, OuterRef, Q

from .forms import QuestionFilterForm
from .models import Favorite, Question, WrongQuestion


def filtered_questions(params, base_queryset=None):
    queryset = base_queryset if base_queryset is not None else Question.objects.all()
    queryset = queryset.filter(
        status=Question.Status.PUBLISHED,
        paper__status="published",
    )
    form = QuestionFilterForm(params)
    if not form.is_valid():
        return queryset.none(), form

    data = form.cleaned_data
    if data["edition"]:
        queryset = queryset.filter(paper__edition=data["edition"])
    if data["stage"]:
        queryset = queryset.filter(paper__stage=data["stage"])
    if data["question_type"]:
        queryset = queryset.filter(question_type=data["question_type"])
    if data["knowledge"]:
        queryset = queryset.filter(knowledge_points__slug__in=data["knowledge"])
    if data["q"]:
        keyword = data["q"].strip()
        queryset = queryset.filter(
            Q(search_text__icontains=keyword)
            | Q(knowledge_points__name__icontains=keyword)
        )

    return (
        queryset.select_related("paper")
        .prefetch_related("knowledge_points")
        .distinct(),
        form,
    )


def with_user_flags(queryset, user):
    if not user.is_authenticated:
        return queryset.annotate(
            is_favorite=Exists(Favorite.objects.none()),
            is_wrong=Exists(WrongQuestion.objects.none()),
        )
    return queryset.annotate(
        is_favorite=Exists(
            Favorite.objects.filter(user=user, question_id=OuterRef("pk"))
        ),
        is_wrong=Exists(
            WrongQuestion.objects.filter(user=user, question_id=OuterRef("pk"))
        ),
    )
```

- [ ] **Step 5: Run query tests and commit**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_queries
```

Expected: five tests pass.

Commit:

```powershell
git add question_bank/forms.py question_bank/queries.py question_bank/tests/test_queries.py
git commit -m "feat: add question filters and search query"
```

## Task 5: Build public pages, Markdown rendering, and local KaTeX assets

**Files:**

- Modify: `config/settings.py`
- Modify: `config/urls.py`
- Create: `question_bank/urls.py`
- Create: `question_bank/views.py`
- Create: `question_bank/templatetags/__init__.py`
- Create: `question_bank/templatetags/content.py`
- Create: `templates/base.html`
- Create: `templates/home.html`
- Create: `templates/404.html`
- Create: `templates/question_bank/_filters.html`
- Create: `templates/question_bank/_question_card.html`
- Create: `templates/question_bank/paper_list.html`
- Create: `templates/question_bank/paper_detail.html`
- Create: `templates/question_bank/question_detail.html`
- Create: `static/js/math.js`
- Create: `static/css/site.css`
- Create: `question_bank/tests/test_views.py`

**Interfaces:**

- Consumes: `filtered_questions()` and `with_user_flags()` from Task 4.
- Produces: named routes `home`, `paper-list`, `search`, `paper-detail`, and `question-detail`.
- Produces: template filter `render_markdown(value) -> SafeString`.

- [ ] **Step 1: Write failing public-page and Markdown tests**

Create `question_bank/tests/test_views.py`:

```python
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from question_bank.models import Paper, Question
from question_bank.templatetags.content import render_markdown


class PublicPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        reviewer = get_user_model().objects.create_user("view-reviewer")
        cls.paper = Paper.objects.create(
            edition=17,
            stage="preliminary",
            original_category_label="非数学A类",
            title="第17届非数学A类初赛",
            status="published",
        )
        cls.question = Question.objects.create(
            paper=cls.paper,
            question_no="1",
            sort_order=1,
            question_type="calculation",
            stem_md=r"计算 \(\lim_{x\to0}x\)。",
            answer_md="0",
            solution_md="极限等于零。",
            source_page=1,
            text_checked=True,
            formula_checked=True,
            solution_checked=True,
            reviewed_by=reviewer,
            status="published",
        )
        cls.draft_paper = Paper.objects.create(
            edition=16,
            stage="final",
            original_category_label="非数学类",
            title="未发布试卷",
        )

    def test_home_and_paper_list_are_public(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        response = self.client.get(reverse("paper-list"))
        self.assertContains(response, self.paper.title)
        self.assertNotContains(response, self.draft_paper.title)

    def test_search_returns_matching_question(self):
        response = self.client.get(reverse("search"), {"q": "极限等于零"})

        self.assertContains(response, "第1题")
        self.assertContains(response, "极限等于零")

    def test_empty_search_does_not_list_every_question(self):
        response = self.client.get(reverse("search"))

        self.assertNotContains(response, "第1题")

    def test_paper_and_question_details_only_show_published_content(self):
        self.assertEqual(
            self.client.get(reverse("paper-detail", args=[self.paper.pk])).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("question-detail", args=[self.question.pk])).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("paper-detail", args=[self.draft_paper.pk])).status_code,
            404,
        )

    def test_markdown_escapes_raw_html_and_keeps_latex(self):
        rendered = str(render_markdown(r"<script>alert(1)</script> \(x^2\)"))

        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn(r"\(x^2\)", rendered)
```

- [ ] **Step 2: Run the tests to verify missing routes and template tag**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_views
```

Expected: FAIL because `question_bank.templatetags.content` and the named routes do not exist.

- [ ] **Step 3: Add local Bootstrap and KaTeX static roots**

Replace the `STATICFILES_DIRS` assignment in `config/settings.py` with:

```python
STATICFILES_DIRS = [
    BASE_DIR / "static",
    ("vendor/bootstrap", BASE_DIR / "node_modules" / "bootstrap" / "dist"),
    ("vendor/katex", BASE_DIR / "node_modules" / "katex" / "dist"),
]
```

- [ ] **Step 4: Implement safe Markdown rendering**

Create empty `question_bank/templatetags/__init__.py`.

Create `question_bank/templatetags/content.py`:

```python
from html import escape

import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def render_markdown(value):
    escaped = escape(value or "")
    rendered = markdown.markdown(
        escaped,
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html5",
    )
    return mark_safe(rendered)
```

- [ ] **Step 5: Implement public views and routes**

Create `question_bank/views.py`:

```python
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .forms import QuestionFilterForm
from .models import Paper, Question
from .queries import filtered_questions, with_user_flags


def home(request):
    return render(
        request,
        "home.html",
        {"filter_form": QuestionFilterForm(), "editions": range(1, 18)},
    )


def _listing_response(request, force_questions=False):
    questions, form = filtered_questions(request.GET)
    question_mode = force_questions or bool(
        request.GET.get("q")
        or request.GET.get("question_type")
        or request.GET.getlist("knowledge")
    )
    empty_search = force_questions and not any(
        (
            request.GET.get("q", "").strip(),
            request.GET.get("edition"),
            request.GET.get("stage"),
            request.GET.get("question_type"),
            request.GET.getlist("knowledge"),
        )
    )
    if empty_search:
        questions = questions.none()

    if question_mode:
        questions = with_user_flags(questions, request.user)
        page_obj = Paginator(questions, 20).get_page(request.GET.get("page"))
    else:
        papers = Paper.objects.filter(status=Paper.Status.PUBLISHED)
        if form.is_valid():
            if form.cleaned_data["edition"]:
                papers = papers.filter(edition=form.cleaned_data["edition"])
            if form.cleaned_data["stage"]:
                papers = papers.filter(stage=form.cleaned_data["stage"])
        else:
            papers = papers.none()
        page_obj = Paginator(papers, 20).get_page(request.GET.get("page"))

    return render(
        request,
        "question_bank/paper_list.html",
        {
            "filter_form": form,
            "page_obj": page_obj,
            "question_mode": question_mode,
            "search_page": force_questions,
        },
    )


def paper_list(request):
    return _listing_response(request)


def search(request):
    return _listing_response(request, force_questions=True)


def paper_detail(request, pk):
    paper = get_object_or_404(Paper, pk=pk, status=Paper.Status.PUBLISHED)
    questions = Question.objects.filter(
        paper=paper, status=Question.Status.PUBLISHED
    ).select_related("paper").prefetch_related("knowledge_points")
    questions = with_user_flags(questions, request.user)
    return render(
        request,
        "question_bank/paper_detail.html",
        {"paper": paper, "questions": questions},
    )


def question_detail(request, pk):
    queryset = with_user_flags(
        Question.objects.filter(
            status=Question.Status.PUBLISHED,
            paper__status=Paper.Status.PUBLISHED,
        ).select_related("paper").prefetch_related("knowledge_points"),
        request.user,
    )
    question = get_object_or_404(queryset, pk=pk)
    siblings = Question.objects.filter(
        paper=question.paper, status=Question.Status.PUBLISHED
    )
    previous_question = siblings.filter(sort_order__lt=question.sort_order).last()
    next_question = siblings.filter(sort_order__gt=question.sort_order).first()
    return render(
        request,
        "question_bank/question_detail.html",
        {
            "question": question,
            "previous_question": previous_question,
            "next_question": next_question,
        },
    )


def not_found(request, exception):
    return render(request, "404.html", status=404)
```

Create `question_bank/urls.py`:

```python
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("papers/", views.paper_list, name="paper-list"),
    path("papers/<int:pk>/", views.paper_detail, name="paper-detail"),
    path("questions/<int:pk>/", views.question_detail, name="question-detail"),
    path("search/", views.search, name="search"),
]
```

Replace `config/urls.py` with:

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("question_bank.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "question_bank.views.not_found"
```

- [ ] **Step 6: Create the base layout and formula bootstrap**

Create `templates/base.html`:

```html
{% load static %}
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="第1—17届全国大学生数学竞赛非数学A类真题与详细解析">
  <title>{% block title %}非数学A类真题库{% endblock %}</title>
  <link rel="stylesheet" href="{% static 'vendor/bootstrap/css/bootstrap.min.css' %}">
  <link rel="stylesheet" href="{% static 'vendor/katex/katex.min.css' %}">
  <link rel="stylesheet" href="{% static 'css/site.css' %}">
</head>
<body>
  <nav class="navbar navbar-expand-lg border-bottom bg-white sticky-top" aria-label="主导航">
    <div class="container site-container">
      <a class="navbar-brand fw-semibold" href="{% url 'home' %}">非数学A类真题库</a>
      <div class="d-flex gap-3 align-items-center">
        <a href="{% url 'paper-list' %}">真题库</a>
        {% if user.is_authenticated %}
          <a href="/me/favorites/">收藏</a>
          <a href="/me/wrong-questions/">错题</a>
          <form method="post" action="/account/logout/" class="m-0">
            {% csrf_token %}<button class="btn btn-link p-0" type="submit">退出</button>
          </form>
        {% else %}
          <a href="/account/login/">登录</a>
        {% endif %}
      </div>
    </div>
  </nav>
  <main class="container site-container py-4">
    {% for message in messages %}<div class="alert alert-info">{{ message }}</div>{% endfor %}
    {% block content %}{% endblock %}
  </main>
  <script defer src="{% static 'vendor/katex/katex.min.js' %}"></script>
  <script defer src="{% static 'vendor/katex/contrib/auto-render.min.js' %}"></script>
  <script defer src="{% static 'js/math.js' %}"></script>
</body>
</html>
```

Create `static/js/math.js`:

```javascript
document.addEventListener("DOMContentLoaded", () => {
  if (!window.renderMathInElement) return;
  window.renderMathInElement(document.body, {
    delimiters: [
      { left: "\\[", right: "\\]", display: true },
      { left: "\\(", right: "\\)", display: false }
    ],
    throwOnError: false,
    errorCallback: (message) => console.error("KaTeX:", message)
  });
});
```

Create `static/css/site.css`:

```css
:root { --site-max: 1200px; }
body { background: #f7f7f5; color: #202124; }
.site-container { max-width: var(--site-max); }
.question-card { background: #fff; border: 1px solid #deded8; border-radius: .75rem; }
.question-content { line-height: 1.85; overflow-wrap: anywhere; }
.question-content img { max-width: 100%; height: auto; }
.question-content .katex-display { overflow-x: auto; overflow-y: hidden; padding-block: .4rem; }
.question-content table { display: block; max-width: 100%; overflow-x: auto; }
a { color: #1458a6; }
```

- [ ] **Step 7: Create page and partial templates**

Create `templates/home.html`:

```html
{% extends "base.html" %}
{% block title %}非数学A类真题库{% endblock %}
{% block content %}
<section class="py-5 text-center">
  <p class="text-secondary mb-2">仅收录第1—17届非数学A类范围</p>
  <h1 class="display-6 fw-bold mb-4">初赛、决赛真题与详细解析</h1>
  <form action="{% url 'search' %}" method="get" class="row g-2 justify-content-center">
    <div class="col-12 col-md-7">{{ filter_form.q }}</div>
    <div class="col-auto"><button class="btn btn-primary" type="submit">搜题</button></div>
  </form>
  <div class="d-flex justify-content-center gap-2 mt-3">
    <a class="btn btn-outline-primary" href="{% url 'paper-list' %}?stage=preliminary">初赛真题</a>
    <a class="btn btn-outline-primary" href="{% url 'paper-list' %}?stage=final">决赛真题</a>
  </div>
</section>
<section aria-labelledby="edition-title">
  <h2 id="edition-title" class="h5 mb-3">按届数查看</h2>
  <div class="d-flex flex-wrap gap-2">
    {% for number in editions %}<a class="btn btn-outline-secondary" href="{% url 'paper-list' %}?edition={{ number }}">第{{ number }}届</a>{% endfor %}
  </div>
</section>
{% endblock %}
```

Create `templates/question_bank/_filters.html`:

```html
<form method="get" class="filter-panel">
  <div class="mb-3"><label class="form-label" for="{{ filter_form.q.id_for_label }}">关键词</label>{{ filter_form.q }}</div>
  <div class="mb-3"><label class="form-label" for="{{ filter_form.edition.id_for_label }}">届数</label>{{ filter_form.edition }}</div>
  <div class="mb-3"><label class="form-label" for="{{ filter_form.stage.id_for_label }}">阶段</label>{{ filter_form.stage }}</div>
  <div class="mb-3"><label class="form-label" for="{{ filter_form.question_type.id_for_label }}">题型</label>{{ filter_form.question_type }}</div>
  <details class="mb-3" {% if filter_form.knowledge.value %}open{% endif %}>
    <summary class="mb-2">知识点</summary>{{ filter_form.knowledge }}
  </details>
  <div class="d-flex gap-2">
    <button class="btn btn-primary" type="submit">筛选</button>
    <a class="btn btn-outline-secondary" href="{% if search_page %}{% url 'search' %}{% else %}{% url 'paper-list' %}{% endif %}">清空</a>
  </div>
</form>
```

Create `templates/question_bank/_question_card.html`:

```html
{% load content %}
<article class="question-card p-3 p-md-4 mb-3" id="question-{{ question.pk }}">
  <header class="d-flex flex-wrap justify-content-between gap-2 mb-3">
    <div>
      <a class="fw-semibold" href="{% url 'question-detail' question.pk %}">第{{ question.question_no }}题</a>
      <span class="badge text-bg-light">{{ question.get_question_type_display }}</span>
    </div>
    <a class="small" href="{% url 'paper-detail' question.paper.pk %}">{{ question.paper.title }}</a>
  </header>
  <div class="question-content">{{ question.stem_md|render_markdown }}</div>
  <div class="d-flex flex-wrap gap-2 my-3">
    {% for point in question.knowledge_points.all %}<span class="badge rounded-pill text-bg-secondary">{{ point.name }}</span>{% endfor %}
  </div>
  <details>
    <summary class="btn btn-outline-primary">查看答案与解析</summary>
    {% if question.answer_md %}<div class="question-content mt-3"><strong>答案：</strong>{{ question.answer_md|render_markdown }}</div>{% endif %}
    <div class="question-content mt-3">{{ question.solution_md|render_markdown }}</div>
  </details>
</article>
```

Create `templates/question_bank/paper_list.html`:

```html
{% extends "base.html" %}
{% load content %}
{% block title %}{% if search_page %}搜题{% else %}真题库{% endif %}{% endblock %}
{% block content %}
<div class="row g-4">
  <aside class="col-12 col-lg-3"><div class="question-card p-3">{% include "question_bank/_filters.html" %}</div></aside>
  <section class="col-12 col-lg-9">
    <h1 class="h3 mb-3">{% if search_page %}搜题结果{% elif question_mode %}题目结果{% else %}真题库{% endif %}</h1>
    {% if question_mode %}
      {% for question in page_obj %}{% include "question_bank/_question_card.html" %}{% empty %}<p>没有符合条件的题目。</p>{% endfor %}
    {% else %}
      <div class="row g-3">
        {% for paper in page_obj %}
          <div class="col-12 col-md-6"><article class="question-card p-4 h-100"><p class="text-secondary">第{{ paper.edition }}届 · {{ paper.get_stage_display }}</p><h2 class="h5"><a href="{% url 'paper-detail' paper.pk %}">{{ paper.title }}</a></h2><p class="mb-0">原卷类别：{{ paper.original_category_label }}</p></article></div>
        {% empty %}<p>没有符合条件的试卷。</p>{% endfor %}
      </div>
    {% endif %}
    {% if page_obj.paginator.num_pages > 1 %}
      <nav class="d-flex justify-content-between mt-4" aria-label="分页">
        {% if page_obj.has_previous %}<a href="{% querystring page=page_obj.previous_page_number %}">上一页</a>{% else %}<span></span>{% endif %}
        <span>第{{ page_obj.number }}页，共{{ page_obj.paginator.num_pages }}页</span>
        {% if page_obj.has_next %}<a href="{% querystring page=page_obj.next_page_number %}">下一页</a>{% else %}<span></span>{% endif %}
      </nav>
    {% endif %}
  </section>
</div>
{% endblock %}
```

Create `templates/question_bank/paper_detail.html`:

```html
{% extends "base.html" %}
{% block title %}{{ paper.title }}{% endblock %}
{% block content %}
<header class="mb-4">
  <p class="text-secondary mb-2">第{{ paper.edition }}届 · {{ paper.get_stage_display }} · {{ paper.original_category_label }}</p>
  <div class="d-flex flex-wrap justify-content-between gap-3"><h1 class="h2">{{ paper.title }}</h1>{% if paper.pdf_file %}<a class="btn btn-outline-primary" href="{% url 'paper-download' paper.pk %}">下载PDF</a>{% endif %}</div>
</header>
<nav class="question-number-nav d-flex gap-2 overflow-x-auto mb-3" aria-label="题号导航">
  {% for question in questions %}<a class="btn btn-sm btn-outline-secondary" href="#question-{{ question.pk }}">{{ question.question_no }}</a>{% endfor %}
</nav>
{% for question in questions %}{% include "question_bank/_question_card.html" %}{% empty %}<p>这份试卷还没有已发布题目。</p>{% endfor %}
{% endblock %}
```

Create `templates/question_bank/question_detail.html`:

```html
{% extends "base.html" %}
{% block title %}{{ question.paper.title }} 第{{ question.question_no }}题{% endblock %}
{% block content %}
<p><a href="{% url 'paper-detail' question.paper.pk %}">← {{ question.paper.title }}</a></p>
{% include "question_bank/_question_card.html" %}
<nav class="d-flex justify-content-between mt-4" aria-label="上下题">
  {% if previous_question %}<a href="{% url 'question-detail' previous_question.pk %}">上一题</a>{% else %}<span></span>{% endif %}
  {% if next_question %}<a href="{% url 'question-detail' next_question.pk %}">下一题</a>{% endif %}
</nav>
{% endblock %}
```

Create `templates/404.html`:

```html
{% extends "base.html" %}
{% block title %}页面不存在{% endblock %}
{% block content %}<h1 class="h2">页面不存在</h1><p><a href="{% url 'paper-list' %}">返回真题库</a>或<a href="{% url 'search' %}">搜索题目</a>。</p>{% endblock %}
```

- [ ] **Step 8: Run public-page tests and collect static files**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_views
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
```

Expected: five tests pass; `collectstatic` copies Bootstrap, KaTeX, and site assets without warnings.

- [ ] **Step 9: Commit public pages**

```powershell
git add config question_bank templates static package.json package-lock.json
git commit -m "feat: add public question bank pages"
```

## Task 6: Add registration, login, favorites, and wrong-question pages

**Files:**

- Create: `accounts/forms.py`
- Create: `accounts/views.py`
- Create: `accounts/urls.py`
- Modify: `accounts/tests.py`
- Modify: `config/urls.py`
- Modify: `question_bank/views.py`
- Modify: `question_bank/urls.py`
- Modify: `templates/base.html`
- Modify: `templates/question_bank/_question_card.html`
- Create: `templates/account/register.html`
- Create: `templates/registration/login.html`
- Create: `templates/question_bank/favorites.html`
- Create: `templates/question_bank/wrong_questions.html`

**Interfaces:**

- Consumes: `filtered_questions()` and `with_user_flags()`.
- Produces: namespaced routes `accounts:login`, `accounts:logout`, and `accounts:register`.
- Produces: POST-only routes `favorite-add`, `favorite-remove`, `wrong-add`, and `wrong-remove`.
- Produces: login-required routes `favorites` and `wrong-questions`.

- [ ] **Step 1: Extend tests for authentication and user-owned records**

Replace `accounts/tests.py` with:

```python
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AccountTests(TestCase):
    def test_project_uses_custom_user_model(self):
        user = get_user_model().objects.create_user("alice", password="safe-pass-123")

        self.assertEqual(user._meta.label, "accounts.User")
        self.assertTrue(user.check_password("safe-pass-123"))

    def test_registration_logs_user_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "new-user",
                "password1": "safe-pass-987",
                "password2": "safe-pass-987",
            },
        )

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), get_user_model().objects.get(username="new-user").pk)
```

Append to `question_bank/tests/test_views.py`:

```python
from question_bank.models import Favorite, WrongQuestion


class UserQuestionListTests(PublicPageTests):
    def setUp(self):
        self.user = get_user_model().objects.create_user("collector", password="pass-12345")

    def test_anonymous_user_cannot_add_favorite(self):
        response = self.client.post(reverse("favorite-add", args=[self.question.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_add_and_remove_favorite_are_idempotent(self):
        self.client.force_login(self.user)
        add_url = reverse("favorite-add", args=[self.question.pk])
        remove_url = reverse("favorite-remove", args=[self.question.pk])

        self.client.post(add_url)
        self.client.post(add_url)
        self.assertEqual(Favorite.objects.filter(user=self.user, question=self.question).count(), 1)

        self.client.post(remove_url)
        self.client.post(remove_url)
        self.assertFalse(Favorite.objects.filter(user=self.user, question=self.question).exists())

    def test_user_only_sees_own_favorites_and_wrong_questions(self):
        other = get_user_model().objects.create_user("other")
        Favorite.objects.create(user=other, question=self.question)
        WrongQuestion.objects.create(user=other, question=self.question)
        self.client.force_login(self.user)

        self.assertNotContains(self.client.get(reverse("favorites")), "第1题")
        self.assertNotContains(self.client.get(reverse("wrong-questions")), "第1题")

    def test_wrong_question_add_and_remove(self):
        self.client.force_login(self.user)

        self.client.post(reverse("wrong-add", args=[self.question.pk]))
        self.assertTrue(WrongQuestion.objects.filter(user=self.user, question=self.question).exists())
        self.client.post(reverse("wrong-remove", args=[self.question.pk]))
        self.assertFalse(WrongQuestion.objects.filter(user=self.user, question=self.question).exists())
```

- [ ] **Step 2: Run tests to verify routes are missing**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test accounts question_bank.tests.test_views.UserQuestionListTests
```

Expected: FAIL with `NoReverseMatch` for `accounts:register` and `favorite-add`.

- [ ] **Step 3: Implement registration and account routes**

Create `accounts/forms.py`:

```python
from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)
```

Create `accounts/views.py`:

```python
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegistrationForm


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("home")
    return render(request, "account/register.html", {"form": form})
```

Create `accounts/urls.py`:

```python
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
]
```

Add the account include to `config/urls.py` immediately after the admin route:

```python
path("account/", include("accounts.urls")),
```

- [ ] **Step 4: Implement idempotent add/remove actions and personal lists**

Append to the imports in `question_bank/views.py`:

```python
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import Favorite, WrongQuestion
```

Append to `question_bank/views.py`:

```python
def _return_url(request, question):
    candidate = request.POST.get("next", "")
    if candidate and url_has_allowed_host_and_scheme(
        candidate, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return candidate
    return reverse("question-detail", args=[question.pk])


def _published_question(pk):
    return get_object_or_404(
        Question,
        pk=pk,
        status=Question.Status.PUBLISHED,
        paper__status=Paper.Status.PUBLISHED,
    )


@login_required
@require_POST
def favorite_add(request, pk):
    question = _published_question(pk)
    Favorite.objects.get_or_create(user=request.user, question=question)
    messages.success(request, "已加入收藏。")
    return redirect(_return_url(request, question))


@login_required
@require_POST
def favorite_remove(request, pk):
    question = _published_question(pk)
    Favorite.objects.filter(user=request.user, question=question).delete()
    messages.success(request, "已取消收藏。")
    return redirect(_return_url(request, question))


@login_required
@require_POST
def wrong_add(request, pk):
    question = _published_question(pk)
    WrongQuestion.objects.get_or_create(user=request.user, question=question)
    messages.success(request, "已加入错题本。")
    return redirect(_return_url(request, question))


@login_required
@require_POST
def wrong_remove(request, pk):
    question = _published_question(pk)
    WrongQuestion.objects.filter(user=request.user, question=question).delete()
    messages.success(request, "已移出错题本。")
    return redirect(_return_url(request, question))


def _personal_list(request, relation, template_name):
    base = Question.objects.filter(**{f"{relation}__user": request.user})
    questions, form = filtered_questions(request.GET, base_queryset=base)
    questions = with_user_flags(questions, request.user)
    page_obj = Paginator(questions, 20).get_page(request.GET.get("page"))
    return render(
        request,
        template_name,
        {"filter_form": form, "page_obj": page_obj},
    )


@login_required
def favorites(request):
    return _personal_list(request, "favorited_by", "question_bank/favorites.html")


@login_required
def wrong_questions(request):
    return _personal_list(request, "marked_wrong_by", "question_bank/wrong_questions.html")
```

Append to `question_bank/urls.py` before the closing bracket:

```python
path("questions/<int:pk>/favorite/add/", views.favorite_add, name="favorite-add"),
path("questions/<int:pk>/favorite/remove/", views.favorite_remove, name="favorite-remove"),
path("questions/<int:pk>/wrong/add/", views.wrong_add, name="wrong-add"),
path("questions/<int:pk>/wrong/remove/", views.wrong_remove, name="wrong-remove"),
path("me/favorites/", views.favorites, name="favorites"),
path("me/wrong-questions/", views.wrong_questions, name="wrong-questions"),
```

- [ ] **Step 5: Add account templates**

Create `templates/registration/login.html`:

```html
{% extends "base.html" %}
{% block title %}登录{% endblock %}
{% block content %}
<div class="mx-auto question-card p-4" style="max-width: 32rem">
  <h1 class="h3 mb-3">登录</h1>
  <form method="post">{% csrf_token %}{{ form.as_p }}{% if next %}<input type="hidden" name="next" value="{{ next }}">{% endif %}<button class="btn btn-primary" type="submit">登录</button></form>
  <p class="mt-3 mb-0">没有账号？<a href="{% url 'accounts:register' %}">注册</a></p>
</div>
{% endblock %}
```

Create `templates/account/register.html`:

```html
{% extends "base.html" %}
{% block title %}注册{% endblock %}
{% block content %}
<div class="mx-auto question-card p-4" style="max-width: 32rem">
  <h1 class="h3 mb-3">注册</h1>
  <form method="post">{% csrf_token %}{{ form.as_p }}<button class="btn btn-primary" type="submit">创建账号</button></form>
</div>
{% endblock %}
```

- [ ] **Step 6: Add favorite/wrong controls and list templates**

Append the following immediately before `</article>` in `templates/question_bank/_question_card.html`:

```html
<footer class="d-flex flex-wrap gap-2 mt-3">
  {% if user.is_authenticated %}
    <form method="post" action="{% if question.is_favorite %}{% url 'favorite-remove' question.pk %}{% else %}{% url 'favorite-add' question.pk %}{% endif %}">
      {% csrf_token %}<input type="hidden" name="next" value="{{ request.get_full_path }}"><button class="btn btn-sm btn-outline-primary" type="submit">{% if question.is_favorite %}取消收藏{% else %}收藏{% endif %}</button>
    </form>
    <form method="post" action="{% if question.is_wrong %}{% url 'wrong-remove' question.pk %}{% else %}{% url 'wrong-add' question.pk %}{% endif %}">
      {% csrf_token %}<input type="hidden" name="next" value="{{ request.get_full_path }}"><button class="btn btn-sm btn-outline-danger" type="submit">{% if question.is_wrong %}移出错题本{% else %}加入错题本{% endif %}</button>
    </form>
  {% else %}
    <a class="btn btn-sm btn-outline-primary" href="{% url 'accounts:login' %}?next={{ request.path|urlencode }}">登录后收藏或加入错题本</a>
  {% endif %}
</footer>
```

Create `templates/question_bank/favorites.html`:

```html
{% extends "base.html" %}
{% block title %}我的收藏{% endblock %}
{% block content %}
<div class="row g-4"><aside class="col-12 col-lg-3"><div class="question-card p-3">{% include "question_bank/_filters.html" %}</div></aside><section class="col-12 col-lg-9"><h1 class="h3 mb-3">我的收藏</h1>{% for question in page_obj %}{% include "question_bank/_question_card.html" %}{% empty %}<p>还没有收藏题目。</p>{% endfor %}</section></div>
{% endblock %}
```

Create `templates/question_bank/wrong_questions.html`:

```html
{% extends "base.html" %}
{% block title %}我的错题{% endblock %}
{% block content %}
<div class="row g-4"><aside class="col-12 col-lg-3"><div class="question-card p-3">{% include "question_bank/_filters.html" %}</div></aside><section class="col-12 col-lg-9"><h1 class="h3 mb-3">我的错题</h1>{% for question in page_obj %}{% include "question_bank/_question_card.html" %}{% empty %}<p>错题本为空。</p>{% endfor %}</section></div>
{% endblock %}
```

Replace the literal account and personal links in `templates/base.html` with their named forms:

```html
{% if user.is_authenticated %}
  <a href="{% url 'favorites' %}">收藏</a>
  <a href="{% url 'wrong-questions' %}">错题</a>
  <form method="post" action="{% url 'accounts:logout' %}" class="m-0">
    {% csrf_token %}<button class="btn btn-link p-0" type="submit">退出</button>
  </form>
{% else %}
  <a href="{% url 'accounts:login' %}">登录</a>
{% endif %}
```

- [ ] **Step 7: Run authentication and ownership tests**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test accounts question_bank.tests.test_views
```

Expected: all account and public/user page tests pass.

- [ ] **Step 8: Commit user functionality**

```powershell
git add accounts config/urls.py question_bank templates
git commit -m "feat: add accounts favorites and wrong questions"
```

## Task 7: Add validated PDF download

**Files:**

- Modify: `question_bank/views.py`
- Modify: `question_bank/urls.py`
- Create: `question_bank/tests/test_download.py`

**Interfaces:**

- Consumes: `Paper.pdf_file` and `validate_pdf()` from Task 2.
- Produces: `GET /papers/{id}/download/` as `paper-download`.

- [ ] **Step 1: Write failing PDF validation and download tests**

Create `question_bank/tests/test_download.py`:

```python
import tempfile

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from question_bank.models import Paper


class PaperDownloadTests(TestCase):
    def setUp(self):
        self.media = tempfile.TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.media.name)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        self.media.cleanup()

    def test_non_pdf_content_is_rejected(self):
        paper = Paper(
            edition=1,
            stage="preliminary",
            original_category_label="非数学类",
            title="非法文件",
            pdf_file=SimpleUploadedFile("paper.pdf", b"not a pdf", content_type="application/pdf"),
        )

        with self.assertRaises(ValidationError):
            paper.save()

    def test_published_pdf_download_has_safe_headers(self):
        paper = Paper.objects.create(
            edition=17,
            stage="preliminary",
            original_category_label="非数学A类",
            title="第17届非数学A类初赛",
            status="published",
            pdf_file=SimpleUploadedFile("unsafe-name.pdf", b"%PDF-1.4\n%%EOF", content_type="application/pdf"),
        )

        response = self.client.get(reverse("paper-download", args=[paper.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn(".pdf", response["Content-Disposition"])

    def test_missing_or_draft_pdf_returns_404(self):
        paper = Paper.objects.create(
            edition=16,
            stage="final",
            original_category_label="非数学A类",
            title="无PDF试卷",
            status="published",
        )

        self.assertEqual(self.client.get(reverse("paper-download", args=[paper.pk])).status_code, 404)
```

- [ ] **Step 2: Run the test to verify the route is missing**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_download
```

Expected: the validator test passes and download tests fail with `NoReverseMatch`.

- [ ] **Step 3: Implement streaming download with a server-generated name**

Add `FileResponse` to imports in `question_bank/views.py`:

```python
from django.http import FileResponse, Http404
```

Append to `question_bank/views.py`:

```python
def paper_download(request, pk):
    paper = get_object_or_404(Paper, pk=pk, status=Paper.Status.PUBLISHED)
    if not paper.pdf_file:
        raise Http404("PDF not found")
    filename = f"第{paper.edition}届-非数学A类-{paper.get_stage_display()}.pdf"
    return FileResponse(
        paper.pdf_file.open("rb"),
        as_attachment=True,
        filename=filename,
        content_type="application/pdf",
    )
```

Add this route immediately after `paper-detail` in `question_bank/urls.py`:

```python
path("papers/<int:pk>/download/", views.paper_download, name="paper-download"),
```

- [ ] **Step 4: Run PDF tests and commit**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_download
```

Expected: three tests pass.

Commit:

```powershell
git add question_bank/views.py question_bank/urls.py question_bank/tests/test_download.py
git commit -m "feat: add validated PDF downloads"
```

## Task 8: Implement atomic workbook import and KaTeX validation

**Files:**

- Create: `scripts/validate-katex.mjs`
- Create: `question_bank/katex.py`
- Create: `question_bank/management/commands/import_question_bank.py`
- Create: `question_bank/tests/test_import.py`

**Interfaces:**

- Consumes: local `node_modules/katex`, fixed model enums, existing knowledge slugs, and reviewer usernames.
- Produces: `validate_markdown_formulas(items: list[tuple[str, str]]) -> list[str]`.
- Produces: `manage.py import_question_bank --create-templates DIR`.
- Produces: `manage.py import_question_bank --inventory FILE --questions FILE [--dry-run]`.

- [ ] **Step 1: Write failing import tests**

Create `question_bank/tests/test_import.py`:

```python
import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from openpyxl import Workbook

from question_bank.management.commands.import_question_bank import (
    INVENTORY_HEADERS,
    QUESTION_HEADERS,
)
from question_bank.models import KnowledgePoint, Paper, Question


class QuestionBankImportTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.media = self.root / "media"
        self.review = self.root / "review"
        self.media.mkdir()
        self.review.mkdir()
        self.override = override_settings(MEDIA_ROOT=self.media, REVIEW_ROOT=self.review)
        self.override.enable()
        self.reviewer = get_user_model().objects.create_user("import-reviewer")
        self.knowledge = KnowledgePoint.objects.create(
            name="函数极限", slug="function-limit", subject="calculus"
        )

    def tearDown(self):
        self.override.disable()
        self.temp.cleanup()

    def write_workbook(self, path, headers, rows):
        workbook = Workbook()
        sheet = workbook.active
        sheet.append(headers)
        for row in rows:
            sheet.append(row)
        workbook.save(path)

    def valid_files(self):
        pdf = self.media / "edition-17-preliminary.pdf"
        crop = self.review / "q1.png"
        pdf.write_bytes(b"%PDF-1.4\n%%EOF")
        crop.write_bytes(b"fake-png-review-copy")
        return pdf.name, crop.name

    def valid_rows(self):
        pdf_name, crop_name = self.valid_files()
        inventory = [[
            17, "preliminary", "非数学A类", "第17届非数学A类初赛",
            2025, "https://example.test/source", pdf_name, 1,
        ]]
        questions = [[
            17, "preliminary", "1", 1, "calculation", 10,
            "function-limit", "", r"计算 \(\lim_{x\to0}x\)。", "0",
            "由极限定义，结果为 0。", "", 1, crop_name, 0.99,
            True, True, True, 0, 0, self.reviewer.username,
        ]]
        return inventory, questions

    def test_create_templates_writes_both_workbooks(self):
        output = self.root / "templates"

        call_command("import_question_bank", create_templates=str(output))

        self.assertTrue((output / "source_inventory.xlsx").exists())
        self.assertTrue((output / "questions.xlsx").exists())

    def test_valid_import_is_idempotent(self):
        inventory_rows, question_rows = self.valid_rows()
        inventory = self.root / "inventory.xlsx"
        questions = self.root / "questions.xlsx"
        self.write_workbook(inventory, INVENTORY_HEADERS, inventory_rows)
        self.write_workbook(questions, QUESTION_HEADERS, question_rows)

        call_command("import_question_bank", inventory=str(inventory), questions=str(questions))
        call_command("import_question_bank", inventory=str(inventory), questions=str(questions))

        self.assertEqual(Paper.objects.count(), 1)
        self.assertEqual(Question.objects.count(), 1)
        question = Question.objects.get()
        self.assertEqual(question.paper.edition, 17)
        self.assertEqual(question.knowledge_points.get(), self.knowledge)
        self.assertEqual(question.status, "reviewed")

    def test_dry_run_does_not_write(self):
        inventory_rows, question_rows = self.valid_rows()
        inventory = self.root / "inventory.xlsx"
        questions = self.root / "questions.xlsx"
        self.write_workbook(inventory, INVENTORY_HEADERS, inventory_rows)
        self.write_workbook(questions, QUESTION_HEADERS, question_rows)

        call_command(
            "import_question_bank",
            inventory=str(inventory),
            questions=str(questions),
            dry_run=True,
        )

        self.assertFalse(Paper.objects.exists())

    def test_duplicate_question_rolls_back_whole_import(self):
        inventory_rows, question_rows = self.valid_rows()
        question_rows.append(question_rows[0].copy())
        inventory_rows[0][-1] = 2
        inventory = self.root / "inventory.xlsx"
        questions = self.root / "questions.xlsx"
        self.write_workbook(inventory, INVENTORY_HEADERS, inventory_rows)
        self.write_workbook(questions, QUESTION_HEADERS, question_rows)

        with self.assertRaises(CommandError):
            call_command("import_question_bank", inventory=str(inventory), questions=str(questions))

        self.assertFalse(Paper.objects.exists())
        self.assertFalse(Question.objects.exists())

    def test_invalid_latex_rolls_back_whole_import(self):
        inventory_rows, question_rows = self.valid_rows()
        question_rows[0][8] = r"错误公式 \(\frac{1}{\)"
        inventory = self.root / "inventory.xlsx"
        questions = self.root / "questions.xlsx"
        self.write_workbook(inventory, INVENTORY_HEADERS, inventory_rows)
        self.write_workbook(questions, QUESTION_HEADERS, question_rows)

        with self.assertRaises(CommandError):
            call_command("import_question_bank", inventory=str(inventory), questions=str(questions))

        self.assertFalse(Paper.objects.exists())
```

- [ ] **Step 2: Run the tests to verify the command is missing**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_import
```

Expected: FAIL because `import_question_bank.py` does not exist.

- [ ] **Step 3: Add the Node KaTeX validator**

Create `scripts/validate-katex.mjs`:

```javascript
import katex from "../node_modules/katex/dist/katex.mjs";

let input = "";
for await (const chunk of process.stdin) input += chunk;

const formulas = JSON.parse(input);
const errors = [];
formulas.forEach((formula, index) => {
  try {
    katex.renderToString(formula, { throwOnError: true, output: "html" });
  } catch (error) {
    errors.push({ index, message: String(error.message || error) });
  }
});
process.stdout.write(JSON.stringify(errors));
```

Create `question_bank/katex.py`:

```python
import json
import re
import subprocess

from django.conf import settings

FORMULA_RE = re.compile(r"\\\[(.*?)\\\]|\\\((.*?)\\\)", re.DOTALL)


def extract_formulas(markdown_text):
    return [
        block if block is not None else inline
        for block, inline in FORMULA_RE.findall(markdown_text or "")
    ]


def validate_markdown_formulas(items):
    issues = []
    formulas = []
    sources = []

    for source, text in items:
        text = text or ""
        if text.count(r"\(") != text.count(r"\)"):
            issues.append(f"{source}: 行内公式定界符不成对")
        if text.count(r"\[") != text.count(r"\]"):
            issues.append(f"{source}: 块级公式定界符不成对")
        for formula in extract_formulas(text):
            formulas.append(formula)
            sources.append(source)

    if not formulas:
        return issues

    try:
        result = subprocess.run(
            ["node", str(settings.BASE_DIR / "scripts" / "validate-katex.mjs")],
            input=json.dumps(formulas, ensure_ascii=False),
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
            cwd=settings.BASE_DIR,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return [*issues, f"KaTeX 校验器无法运行: {error}"]

    if result.returncode != 0:
        return [*issues, f"KaTeX 校验器退出码 {result.returncode}: {result.stderr.strip()}"]

    for error in json.loads(result.stdout or "[]"):
        issues.append(f"{sources[error['index']]}: {error['message']}")
    return issues
```

- [ ] **Step 4: Implement workbook templates, validation, and atomic upsert**

Create `question_bank/management/commands/import_question_bank.py`:

```python
from collections import Counter
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from openpyxl import Workbook, load_workbook

from question_bank.katex import validate_markdown_formulas
from question_bank.models import (
    MAX_PDF_BYTES,
    KnowledgePoint,
    Paper,
    Question,
    QuestionKnowledgePoint,
)

INVENTORY_HEADERS = [
    "edition", "stage", "original_category_label", "title", "exam_year",
    "source_url", "pdf_file", "question_count",
]
QUESTION_HEADERS = [
    "edition", "stage", "question_no", "sort_order", "question_type", "score",
    "primary_knowledge", "secondary_knowledge", "stem_md", "answer_md",
    "solution_md", "image_files", "source_page", "source_crop", "ocr_confidence",
    "text_checked", "formula_checked", "solution_checked", "unresolved_ocr_items",
    "katex_errors", "reviewer",
]


def as_int(value, label, issues):
    try:
        return int(value)
    except (TypeError, ValueError):
        issues.append(f"{label}: 必须是整数")
        return 0


def as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "是"}


def split_values(value):
    return [item.strip() for item in str(value or "").replace("，", ",").split(",") if item.strip()]


def safe_file(root, relative, label, issues, pdf=False):
    if not relative:
        return
    root = Path(root).resolve()
    target = (root / str(relative)).resolve()
    if not target.is_relative_to(root):
        issues.append(f"{label}: 路径超出允许目录")
        return
    if not target.is_file():
        issues.append(f"{label}: 文件不存在 {relative}")
        return
    if pdf:
        if target.suffix.lower() != ".pdf":
            issues.append(f"{label}: 文件扩展名必须是 .pdf")
        if target.stat().st_size > MAX_PDF_BYTES:
            issues.append(f"{label}: PDF 不能超过 50 MB")
        with target.open("rb") as source:
            if source.read(5) != b"%PDF-":
                issues.append(f"{label}: 文件内容不是 PDF")


class Command(BaseCommand):
    help = "Validate and import non-mathematics A papers and questions from XLSX files."

    def add_arguments(self, parser):
        parser.add_argument("--inventory")
        parser.add_argument("--questions")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--create-templates", dest="create_templates")

    def handle(self, *args, **options):
        if options["create_templates"]:
            self.write_templates(Path(options["create_templates"]))
            return
        if not options["inventory"] or not options["questions"]:
            raise CommandError("必须同时提供 --inventory 和 --questions。")

        paper_rows = self.read_rows(Path(options["inventory"]), INVENTORY_HEADERS, "inventory")
        question_rows = self.read_rows(Path(options["questions"]), QUESTION_HEADERS, "questions")
        issues = []
        papers = self.validate_papers(paper_rows, issues)
        questions = self.validate_questions(question_rows, papers, issues)
        self.validate_counts(papers, questions, issues)

        formula_items = []
        for row in questions:
            label = f"questions 第{row['_line']}行"
            formula_items.extend([
                (f"{label} stem_md", str(row.get("stem_md") or "")),
                (f"{label} answer_md", str(row.get("answer_md") or "")),
                (f"{label} solution_md", str(row.get("solution_md") or "")),
            ])
        issues.extend(validate_markdown_formulas(formula_items))

        if issues:
            raise CommandError("导入校验失败:\n" + "\n".join(f"- {issue}" for issue in issues))
        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(
                f"Dry-run passed: {len(papers)} papers, {len(questions)} questions."
            ))
            return

        with transaction.atomic():
            self.upsert(papers, questions)
        self.stdout.write(self.style.SUCCESS(
            f"Imported {len(papers)} papers and {len(questions)} questions."
        ))

    def write_templates(self, directory):
        directory.mkdir(parents=True, exist_ok=True)
        for filename, headers in (
            ("source_inventory.xlsx", INVENTORY_HEADERS),
            ("questions.xlsx", QUESTION_HEADERS),
        ):
            workbook = Workbook()
            workbook.active.append(headers)
            workbook.save(directory / filename)
        self.stdout.write(self.style.SUCCESS(f"Templates created in {directory}"))

    def read_rows(self, path, required_headers, label):
        if not path.is_file():
            raise CommandError(f"{label}: 文件不存在 {path}")
        worksheet = load_workbook(path, read_only=True, data_only=True).active
        rows = worksheet.iter_rows(values_only=True)
        try:
            first_row = next(rows)
        except StopIteration as error:
            raise CommandError(f"{label}: 工作簿为空") from error
        headers = [str(value or "").strip() for value in first_row]
        missing = [header for header in required_headers if header not in headers]
        if missing:
            raise CommandError(f"{label}: 缺少列 {', '.join(missing)}")
        output = []
        for line, values in enumerate(rows, start=2):
            row = dict(zip(headers, values))
            if any(value not in (None, "") for value in row.values()):
                row["_line"] = line
                output.append(row)
        return output

    def validate_papers(self, rows, issues):
        papers = {}
        valid_stages = {value for value, _ in Paper.Stage.choices}
        for row in rows:
            label = f"inventory 第{row['_line']}行"
            edition = as_int(row.get("edition"), f"{label} edition", issues)
            stage = str(row.get("stage") or "").strip()
            key = (edition, stage)
            if not 1 <= edition <= 17:
                issues.append(f"{label}: edition 必须在 1—17")
            if stage not in valid_stages:
                issues.append(f"{label}: stage 必须是 preliminary 或 final")
            if key in papers:
                issues.append(f"{label}: 重复试卷 {key}")
            if not str(row.get("original_category_label") or "").strip():
                issues.append(f"{label}: original_category_label 不能为空")
            if not str(row.get("title") or "").strip():
                issues.append(f"{label}: title 不能为空")
            row["_edition"] = edition
            row["_stage"] = stage
            question_count = as_int(
                row.get("question_count"), f"{label} question_count", issues
            )
            if question_count < 1:
                issues.append(f"{label}: question_count 必须大于 0")
            row["_question_count"] = question_count
            safe_file(settings.MEDIA_ROOT, row.get("pdf_file"), f"{label} pdf_file", issues, pdf=True)
            papers[key] = row
        return papers

    def validate_questions(self, rows, papers, issues):
        valid_types = {value for value, _ in Question.Type.choices}
        knowledge = {point.slug: point for point in KnowledgePoint.objects.all()}
        users = {user.username: user for user in get_user_model().objects.all()}
        seen = set()

        for row in rows:
            label = f"questions 第{row['_line']}行"
            edition = as_int(row.get("edition"), f"{label} edition", issues)
            stage = str(row.get("stage") or "").strip()
            number = str(row.get("question_no") or "").strip()
            key = (edition, stage, number)
            if (edition, stage) not in papers:
                issues.append(f"{label}: 找不到对应 inventory 试卷")
            if not number:
                issues.append(f"{label}: question_no 不能为空")
            if key in seen:
                issues.append(f"{label}: 重复题号 {key}")
            seen.add(key)
            question_type = str(row.get("question_type") or "").strip()
            if question_type not in valid_types:
                issues.append(f"{label}: 非法 question_type {question_type}")
            if not str(row.get("stem_md") or "").strip():
                issues.append(f"{label}: stem_md 不能为空")
            if not str(row.get("solution_md") or "").strip():
                issues.append(f"{label}: solution_md 不能为空")

            primary = str(row.get("primary_knowledge") or "").strip()
            secondary = split_values(row.get("secondary_knowledge"))
            for slug in [primary, *secondary]:
                if slug not in knowledge:
                    issues.append(f"{label}: 未知知识点 {slug}")
            if primary in secondary:
                issues.append(f"{label}: 主知识点不能重复出现在次知识点")

            reviewer_name = str(row.get("reviewer") or "").strip()
            if reviewer_name and reviewer_name not in users:
                issues.append(f"{label}: reviewer 用户不存在 {reviewer_name}")
            for image in split_values(row.get("image_files")):
                safe_file(settings.MEDIA_ROOT, image, f"{label} image_files", issues)
            safe_file(settings.REVIEW_ROOT, row.get("source_crop"), f"{label} source_crop", issues)

            sort_order = as_int(row.get("sort_order"), f"{label} sort_order", issues)
            source_page = as_int(row.get("source_page"), f"{label} source_page", issues)
            unresolved = as_int(
                row.get("unresolved_ocr_items"), f"{label} unresolved_ocr_items", issues
            )
            katex_errors = as_int(row.get("katex_errors"), f"{label} katex_errors", issues)
            if sort_order < 1:
                issues.append(f"{label}: sort_order 必须大于 0")
            if source_page < 1:
                issues.append(f"{label}: source_page 必须大于 0")
            if unresolved < 0 or katex_errors < 0:
                issues.append(f"{label}: OCR 和 KaTeX 错误数不能为负数")

            row.update({
                "_edition": edition,
                "_stage": stage,
                "_number": number,
                "_sort_order": sort_order,
                "_source_page": source_page,
                "_unresolved": unresolved,
                "_katex_errors": katex_errors,
                "_primary": primary,
                "_secondary": secondary,
                "_reviewer": users.get(reviewer_name),
                "_text_checked": as_bool(row.get("text_checked")),
                "_formula_checked": as_bool(row.get("formula_checked")),
                "_solution_checked": as_bool(row.get("solution_checked")),
            })
        return rows

    def validate_counts(self, papers, questions, issues):
        actual = Counter((row["_edition"], row["_stage"]) for row in questions)
        for key, paper in papers.items():
            if actual[key] != paper["_question_count"]:
                issues.append(
                    f"inventory 第{paper['_line']}行: question_count={paper['_question_count']}，实际={actual[key]}"
                )

    def upsert(self, papers, questions):
        paper_objects = {}
        for key, row in papers.items():
            paper, _ = Paper.objects.update_or_create(
                edition=row["_edition"],
                stage=row["_stage"],
                defaults={
                    "original_category_label": str(row["original_category_label"]).strip(),
                    "title": str(row["title"]).strip(),
                    "exam_year": row.get("exam_year") or None,
                    "source_url": str(row.get("source_url") or "").strip(),
                    "pdf_file": str(row.get("pdf_file") or "").strip(),
                    "status": Paper.Status.REVIEWED,
                },
            )
            paper_objects[key] = paper

        knowledge = {point.slug: point for point in KnowledgePoint.objects.all()}
        for row in questions:
            reviewed = all((
                row["_text_checked"], row["_formula_checked"], row["_solution_checked"],
                row["_reviewer"] is not None, row["_unresolved"] == 0, row["_katex_errors"] == 0,
            ))
            question, _ = Question.objects.update_or_create(
                paper=paper_objects[(row["_edition"], row["_stage"])],
                question_no=row["_number"],
                defaults={
                    "sort_order": row["_sort_order"],
                    "question_type": str(row["question_type"]).strip(),
                    "score": row.get("score") or None,
                    "stem_md": str(row["stem_md"]).strip(),
                    "answer_md": str(row.get("answer_md") or "").strip(),
                    "solution_md": str(row["solution_md"]).strip(),
                    "source_page": row["_source_page"],
                    "source_crop": str(row.get("source_crop") or "").strip(),
                    "text_checked": row["_text_checked"],
                    "formula_checked": row["_formula_checked"],
                    "solution_checked": row["_solution_checked"],
                    "unresolved_ocr_items": row["_unresolved"],
                    "katex_errors": row["_katex_errors"],
                    "reviewed_by": row["_reviewer"],
                    "reviewed_at": timezone.now() if reviewed else None,
                    "status": Question.Status.REVIEWED if reviewed else Question.Status.DRAFT,
                },
            )
            QuestionKnowledgePoint.objects.filter(question=question).delete()
            QuestionKnowledgePoint.objects.create(
                question=question,
                knowledge_point=knowledge[row["_primary"]],
                is_primary=True,
            )
            for slug in row["_secondary"]:
                QuestionKnowledgePoint.objects.create(
                    question=question,
                    knowledge_point=knowledge[slug],
                    is_primary=False,
                )
```

- [ ] **Step 5: Run import tests**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_import
```

Expected: five tests pass, including real KaTeX parsing through local Node.

- [ ] **Step 6: Generate blank operator templates and perform a dry-run**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py import_question_bank --create-templates data/import
```

Expected: `data/import/source_inventory.xlsx` and `data/import/questions.xlsx` are created with exact headers. The files stay ignored by Git because they will contain source material.

- [ ] **Step 7: Commit the import pipeline**

```powershell
git add scripts/validate-katex.mjs question_bank/katex.py question_bank/management/commands/import_question_bank.py question_bank/tests/test_import.py
git commit -m "feat: add atomic XLSX question importer"
```

## Task 9: Add protected source comparison and publish gates to Admin

**Files:**

- Modify: `question_bank/admin.py`
- Modify: `question_bank/tests/test_admin.py`

**Interfaces:**

- Consumes: `settings.REVIEW_ROOT`, `render_markdown()`, and `Question.can_publish()`.
- Produces: source-crop preview and rendered-content preview inside staff-only Django Admin.
- Produces: a bulk publish action that skips questions failing any review gate.

- [ ] **Step 1: Add failing Admin review tests**

Append to `question_bank/tests/test_admin.py`:

```python
import tempfile
from pathlib import Path

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, override_settings

from question_bank.admin import QuestionAdmin
from question_bank.models import Paper, Question


class QuestionAdminReviewTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.review_root = Path(self.temp.name)
        self.override = override_settings(REVIEW_ROOT=self.review_root)
        self.override.enable()
        self.staff = get_user_model().objects.create_superuser(
            "admin-reviewer", "admin@example.test", "pass-12345"
        )
        self.paper = Paper.objects.create(
            edition=17,
            stage="preliminary",
            original_category_label="非数学A类",
            title="第17届非数学A类初赛",
            status="published",
        )
        self.question = Question.objects.create(
            paper=self.paper,
            question_no="1",
            sort_order=1,
            question_type="calculation",
            stem_md=r"计算 \(x^2\)。",
            solution_md="解析",
            source_page=1,
            source_crop="q1.png",
        )
        (self.review_root / "q1.png").write_bytes(b"small-review-image")
        self.model_admin = QuestionAdmin(Question, admin.site)

    def tearDown(self):
        self.override.disable()
        self.temp.cleanup()

    def test_source_preview_is_embedded_without_public_file_url(self):
        preview = str(self.model_admin.source_preview(self.question))

        self.assertIn("data:image/png;base64,", preview)
        self.assertNotIn(str(self.review_root), preview)

    def test_rendered_preview_escapes_html_and_keeps_formula(self):
        self.question.stem_md = r"<script>alert(1)</script> \(x^2\)"

        preview = str(self.model_admin.rendered_preview(self.question))

        self.assertNotIn("<script>", preview)
        self.assertIn(r"\(x^2\)", preview)

    def test_publish_action_skips_unreviewed_question(self):
        request = RequestFactory().post("/admin/")
        request.user = self.staff
        request._messages = type("Messages", (), {"add": lambda *args, **kwargs: None})()

        self.model_admin.publish_reviewed(request, Question.objects.filter(pk=self.question.pk))

        self.question.refresh_from_db()
        self.assertEqual(self.question.status, Question.Status.DRAFT)
```

- [ ] **Step 2: Run the tests to verify preview methods are missing**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_admin.QuestionAdminReviewTests
```

Expected: FAIL with `AttributeError` for `source_preview`.

- [ ] **Step 3: Replace QuestionAdmin with the reviewed implementation**

Add these imports to `question_bank/admin.py`:

```python
import base64
import mimetypes
from pathlib import Path

from django.conf import settings
from django.utils.html import format_html

from .templatetags.content import render_markdown
```

Replace `QuestionAdmin` in `question_bank/admin.py` with:

```python
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "paper", "question_no", "question_type", "review_state", "status"
    )
    list_filter = (
        "paper__edition", "paper__stage", "question_type", "status",
        "text_checked", "formula_checked", "solution_checked",
    )
    search_fields = ("stem_md", "answer_md", "solution_md")
    readonly_fields = ("source_preview", "rendered_preview", "search_text")
    inlines = (QuestionKnowledgeInline,)
    actions = ("publish_reviewed",)
    fieldsets = (
        ("归属", {"fields": ("paper", "question_no", "sort_order", "question_type", "score")}),
        ("内容", {"fields": ("stem_md", "answer_md", "solution_md", "rendered_preview")}),
        ("原卷", {"fields": ("source_page", "source_crop", "source_preview")}),
        ("复核", {"fields": (
            "text_checked", "formula_checked", "solution_checked",
            "unresolved_ocr_items", "katex_errors", "reviewed_by", "reviewed_at", "status",
        )}),
        ("搜索", {"fields": ("search_text",), "classes": ("collapse",)}),
    )

    @admin.display(description="复核状态")
    def review_state(self, obj):
        return "通过" if obj.can_publish() else "未通过"

    @admin.display(description="原卷截图")
    def source_preview(self, obj):
        if not obj.source_crop:
            return "未上传校对截图"
        root = Path(settings.REVIEW_ROOT).resolve()
        path = (root / obj.source_crop).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            return "校对截图不存在"
        if path.stat().st_size > 5 * 1024 * 1024:
            return "校对截图超过 5 MB"
        mime = mimetypes.guess_type(path.name)[0]
        if mime not in {"image/png", "image/jpeg", "image/webp"}:
            return "校对截图格式必须是 PNG、JPEG 或 WebP"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return format_html(
            '<img src="data:{};base64,{}" alt="原卷第{}页截图" style="max-width:100%;height:auto">',
            mime,
            encoded,
            obj.source_page,
        )

    @admin.display(description="网页渲染预览")
    def rendered_preview(self, obj):
        return format_html(
            '<section class="question-preview"><h3>题干</h3>{}<h3>答案</h3>{}<h3>解析</h3>{}</section>',
            render_markdown(obj.stem_md),
            render_markdown(obj.answer_md),
            render_markdown(obj.solution_md),
        )

    @admin.action(description="发布已通过全部复核的题目")
    def publish_reviewed(self, request, queryset):
        published = 0
        skipped = 0
        for question in queryset.select_related("paper", "reviewed_by"):
            if question.can_publish():
                question.status = Question.Status.PUBLISHED
                question.save(update_fields=["status", "search_text", "updated_at"])
                published += 1
            else:
                skipped += 1
        self.message_user(request, f"已发布 {published} 题，跳过 {skipped} 题。")
```

- [ ] **Step 4: Run Admin tests and the full model suite**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_admin question_bank.tests.test_models
```

Expected: all tests pass; an unreviewed question remains a draft after the bulk action.

- [ ] **Step 5: Commit Admin review tools**

```powershell
git add question_bank/admin.py question_bank/tests/test_admin.py
git commit -m "feat: add source comparison and publish gates"
```

## Task 10: Finish responsive layout and accessibility

**Files:**

- Modify: `templates/question_bank/paper_list.html`
- Modify: `templates/question_bank/favorites.html`
- Modify: `templates/question_bank/wrong_questions.html`
- Modify: `static/css/site.css`
- Modify: `question_bank/tests/test_views.py`

**Interfaces:**

- Consumes: existing filter form, question card, and Bootstrap breakpoints.
- Produces: desktop fixed filter column and native mobile filter disclosure below `768px`.
- Produces: 44px touch targets, visible keyboard focus, and horizontally scrollable formulas/tables.

- [ ] **Step 1: Add a failing responsive-markup test**

Append to `PublicPageTests` in `question_bank/tests/test_views.py`:

```python
    def test_list_page_contains_mobile_filter_and_viewport_support(self):
        response = self.client.get(reverse("paper-list"))

        self.assertContains(response, 'name="viewport"')
        self.assertContains(response, 'class="mobile-filter')
        self.assertContains(response, 'class="desktop-filter')
```

- [ ] **Step 2: Run the targeted test to verify mobile markup is absent**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_views.PublicPageTests.test_list_page_contains_mobile_filter_and_viewport_support
```

Expected: FAIL because `mobile-filter` is not present.

- [ ] **Step 3: Replace the filter shell in the paper list**

Replace the opening `<div class="row g-4">` and its following `<aside>` line in `templates/question_bank/paper_list.html` with:

```html
<details class="mobile-filter question-card p-3 mb-3 d-lg-none">
  <summary class="fw-semibold">筛选题目</summary>
  <div class="pt-3">{% include "question_bank/_filters.html" %}</div>
</details>
<div class="row g-4">
  <aside class="desktop-filter col-lg-3 d-none d-lg-block"><div class="question-card p-3 sticky-filter">{% include "question_bank/_filters.html" %}</div></aside>
```

- [ ] **Step 4: Replace the personal-list templates with responsive filter shells**

Replace `templates/question_bank/favorites.html` with:

```html
{% extends "base.html" %}
{% block title %}我的收藏{% endblock %}
{% block content %}
<details class="mobile-filter question-card p-3 mb-3 d-lg-none"><summary class="fw-semibold">筛选收藏</summary><div class="pt-3">{% include "question_bank/_filters.html" %}</div></details>
<div class="row g-4">
  <aside class="desktop-filter col-lg-3 d-none d-lg-block"><div class="question-card p-3 sticky-filter">{% include "question_bank/_filters.html" %}</div></aside>
  <section class="col-12 col-lg-9"><h1 class="h3 mb-3">我的收藏</h1>{% for question in page_obj %}{% include "question_bank/_question_card.html" %}{% empty %}<p>还没有收藏题目。</p>{% endfor %}</section>
</div>
{% endblock %}
```

Replace `templates/question_bank/wrong_questions.html` with:

```html
{% extends "base.html" %}
{% block title %}我的错题{% endblock %}
{% block content %}
<details class="mobile-filter question-card p-3 mb-3 d-lg-none"><summary class="fw-semibold">筛选错题</summary><div class="pt-3">{% include "question_bank/_filters.html" %}</div></details>
<div class="row g-4">
  <aside class="desktop-filter col-lg-3 d-none d-lg-block"><div class="question-card p-3 sticky-filter">{% include "question_bank/_filters.html" %}</div></aside>
  <section class="col-12 col-lg-9"><h1 class="h3 mb-3">我的错题</h1>{% for question in page_obj %}{% include "question_bank/_question_card.html" %}{% empty %}<p>错题本为空。</p>{% endfor %}</section>
</div>
{% endblock %}
```

- [ ] **Step 5: Replace the site stylesheet with final responsive styles**

Replace `static/css/site.css` with:

```css
:root {
  --site-max: 1200px;
  --paper: #ffffff;
  --canvas: #f7f7f5;
  --ink: #202124;
  --line: #deded8;
  --focus: #0d6efd;
}

html { scroll-padding-top: 5.5rem; }
body { background: var(--canvas); color: var(--ink); font-size: 17px; }
.site-container { max-width: var(--site-max); }
.question-card { background: var(--paper); border: 1px solid var(--line); border-radius: .75rem; }
.question-content { line-height: 1.85; overflow-wrap: anywhere; }
.question-content img { max-width: 100%; height: auto; }
.question-content .katex-display { overflow-x: auto; overflow-y: hidden; padding-block: .4rem; }
.question-content table { display: block; width: max-content; max-width: 100%; overflow-x: auto; }
.question-number-nav { position: sticky; top: 4.25rem; z-index: 10; background: var(--canvas); padding-block: .5rem; }
.sticky-filter { position: sticky; top: 5.25rem; max-height: calc(100vh - 6.25rem); overflow-y: auto; }
.filter-panel ul { list-style: none; padding-left: 0; }
.filter-panel label { display: inline-flex; gap: .45rem; align-items: start; padding-block: .2rem; }
.mobile-filter > summary { min-height: 44px; display: flex; align-items: center; cursor: pointer; }
.btn, button, input, select, summary, a { touch-action: manipulation; }
:focus-visible { outline: 3px solid var(--focus); outline-offset: 3px; }
a { color: #1458a6; }

@media (max-width: 767.98px) {
  body { font-size: 16px; }
  .site-container { padding-inline: 1rem; }
  .question-card { border-radius: .6rem; }
  .question-card .btn, .question-card button { min-height: 44px; }
  .navbar .site-container { align-items: flex-start; }
}
```

- [ ] **Step 6: Run responsive markup tests and manual viewport checks**

Run:

```powershell
.\.venv\Scripts\python.exe manage.py test question_bank.tests.test_views
.\.venv\Scripts\python.exe manage.py runserver
```

Expected automated result: all view tests pass.

Open the paper list, paper detail, question detail, favorites, and wrong-question pages at these browser viewport widths:

```text
375 × 812
768 × 1024
1440 × 900
```

Verify:

- `375px`: filters appear inside the native disclosure; no page-level horizontal scrollbar appears.
- `768px`: content remains single-column and formulas scroll inside their own container.
- `1440px`: the 260px-equivalent Bootstrap filter column remains visible and sticky.
- Keyboard Tab shows a visible focus outline on navigation, filters, disclosure, solution, favorite, and wrong-question controls.

- [ ] **Step 7: Commit responsive behavior**

```powershell
git add templates/question_bank static/css/site.css question_bank/tests/test_views.py
git commit -m "feat: finish responsive accessible layout"
```

## Task 11: Add production settings, single-server deployment, backup, and final verification

**Files:**

- Modify: `config/settings.py`
- Create: `deploy/Caddyfile`
- Create: `deploy/cmc-a.service`
- Create: `deploy/backup.sh`
- Create: `deploy/cmc-a-backup.cron`

**Interfaces:**

- Consumes: Gunicorn WSGI entry point `config.wsgi:application`.
- Produces: Caddy static/media serving and reverse proxy to `127.0.0.1:8000`.
- Produces: daily off-process SQLite and media backups retained for 14 days.

- [ ] **Step 1: Add production security settings**

Append to `config/settings.py`:

```python
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 0 if DEBUG else 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
```

- [ ] **Step 2: Add the Caddy and systemd definitions**

Create `deploy/Caddyfile`:

```caddyfile
{$SITE_ADDRESS} {
    encode zstd gzip

    handle_path /static/* {
        root * /srv/cmc-a/staticfiles
        file_server
    }

    handle_path /media/* {
        root * /srv/cmc-a/media
        file_server
    }

    reverse_proxy 127.0.0.1:8000
}
```

Create `deploy/cmc-a.service`:

```ini
[Unit]
Description=Non-mathematics A question bank
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/srv/cmc-a
EnvironmentFile=/etc/cmc-a.env
ExecStart=/srv/cmc-a/.venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8000 config.wsgi:application
Restart=on-failure
RestartSec=5
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

- [ ] **Step 3: Add bounded backup scripts**

Create `deploy/backup.sh`:

```sh
#!/bin/sh
set -eu

app_root=/srv/cmc-a
backup_root=/var/backups/cmc-a
stamp=$(date +%Y%m%d-%H%M%S)

install -d -m 0700 "$backup_root"
sqlite3 "$app_root/db.sqlite3" ".backup '$backup_root/db-$stamp.sqlite3'"
tar -czf "$backup_root/files-$stamp.tar.gz" -C "$app_root" media data/review data/import
find "$backup_root" -maxdepth 1 -type f -mtime +14 -delete
```

Create `deploy/cmc-a-backup.cron`:

```cron
17 3 * * * root /usr/local/sbin/cmc-a-backup
```

- [ ] **Step 4: Run all local verification**

Run in PowerShell:

```powershell
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
npm.cmd audit --omit=dev
$env:DJANGO_DEBUG='0'
$env:DJANGO_SECRET_KEY='1f7d9d21494201f6f4acfc97274e0d4934809e77d73c879dc702fa659569b1ac'
$env:DJANGO_ALLOWED_HOSTS='question-bank.test'
$env:DJANGO_CSRF_TRUSTED_ORIGINS='https://question-bank.test'
.\.venv\Scripts\python.exe manage.py check --deploy
Remove-Item Env:DJANGO_DEBUG,Env:DJANGO_SECRET_KEY,Env:DJANGO_ALLOWED_HOSTS,Env:DJANGO_CSRF_TRUSTED_ORIGINS
```

Expected:

- All Django tests pass.
- Django system checks report no issues.
- `collectstatic` includes `vendor/bootstrap`, `vendor/katex`, `css/site.css`, and `js/math.js`.
- npm reports no known production dependency vulnerability.
- `check --deploy` reports no security warnings.

- [ ] **Step 5: Install runtime dependencies on the Linux server**

After the committed repository has been placed at `/srv/cmc-a`, run:

```sh
sudo apt-get update
sudo apt-get install -y python3.13 python3.13-venv nodejs npm caddy sqlite3
sudo chown -R www-data:www-data /srv/cmc-a
sudo -u www-data python3.13 -m venv /srv/cmc-a/.venv
sudo -u www-data /srv/cmc-a/.venv/bin/python -m pip install -r /srv/cmc-a/requirements.txt
sudo -u www-data sh -c 'cd /srv/cmc-a && npm ci'
sudo -u www-data /srv/cmc-a/.venv/bin/python /srv/cmc-a/manage.py migrate
sudo -u www-data /srv/cmc-a/.venv/bin/python /srv/cmc-a/manage.py collectstatic --noinput
```

Expected: Python, Node, Caddy, SQLite, Python packages, and local Bootstrap/KaTeX assets are installed.

- [ ] **Step 6: Validate Linux deployment files**

Run on the target Linux server from `/srv/cmc-a`:

```sh
sh -n deploy/backup.sh
/srv/cmc-a/.venv/bin/gunicorn --check-config config.wsgi:application
SITE_ADDRESS=localhost caddy validate --config /srv/cmc-a/deploy/Caddyfile
```

Expected: all three commands exit with status 0.

- [ ] **Step 7: Install the service, Caddy route, and backup schedule**

Run on the Linux server. Enter the real domain when prompted:

```sh
read -r -p "Site domain: " CMC_SITE_HOST
CMC_SECRET=$(openssl rand -hex 32)
sudo sh -c "umask 077; printf '%s\n' 'DJANGO_DEBUG=0' 'DJANGO_SECRET_KEY=$CMC_SECRET' 'DJANGO_ALLOWED_HOSTS=$CMC_SITE_HOST' 'DJANGO_CSRF_TRUSTED_ORIGINS=https://$CMC_SITE_HOST' > /etc/cmc-a.env"
sudo install -m 0644 deploy/cmc-a.service /etc/systemd/system/cmc-a.service
sudo install -m 0644 deploy/Caddyfile /etc/caddy/Caddyfile
sudo install -m 0755 deploy/backup.sh /usr/local/sbin/cmc-a-backup
sudo install -m 0644 deploy/cmc-a-backup.cron /etc/cron.d/cmc-a-backup
sudo install -d -m 0755 /etc/systemd/system/caddy.service.d
sudo sh -c "printf '%s\n' '[Service]' 'Environment=SITE_ADDRESS=$CMC_SITE_HOST' > /etc/systemd/system/caddy.service.d/site.conf"
sudo -u www-data /srv/cmc-a/.venv/bin/python manage.py migrate
sudo -u www-data /srv/cmc-a/.venv/bin/python manage.py collectstatic --noinput
sudo systemctl daemon-reload
sudo systemctl enable --now cmc-a caddy
sudo systemctl status cmc-a --no-pager
curl -I "https://$CMC_SITE_HOST/"
```

Expected: both services are active, the final `curl` returns HTTP 200, and Caddy supplies HTTPS.

- [ ] **Step 8: Run the first content-pipeline smoke test**

Run in Windows development:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py seed_knowledge_points
.\.venv\Scripts\python.exe manage.py import_question_bank --create-templates data/import
.\.venv\Scripts\python.exe manage.py runserver
```

Use one text-based paper and one scanned paper to fill the generated workbooks. Then run:

```powershell
.\.venv\Scripts\python.exe manage.py import_question_bank --inventory data/import/source_inventory.xlsx --questions data/import/questions.xlsx --dry-run
.\.venv\Scripts\python.exe manage.py import_question_bank --inventory data/import/source_inventory.xlsx --questions data/import/questions.xlsx
```

Expected: dry-run reports the exact paper and question counts; the real import creates no duplicate rows; Admin shows the private source crop beside the rendered question; only reviewed questions can be published.

- [ ] **Step 9: Complete the acceptance checklist**

Verify each requirement against the running application:

```text
[ ] Home, paper list, paper detail, question detail, search, login, register,
    favorites, wrong questions, Admin, and 404 pages work.
[ ] Edition accepts only 1–17; stage accepts only preliminary/final.
[ ] Same-dimension filters use OR; cross-dimension filters use AND.
[ ] No category selector or non-mathematics B/mathematics content exists.
[ ] Online questions render Markdown, images, inline formulas, and block formulas.
[ ] PDF download streams a validated file with a server-generated filename.
[ ] Keyword search covers stem, answer, detailed solution, paper title, and knowledge point.
[ ] Anonymous users can read; only logged-in users can change their own favorite/wrong records.
[ ] Mobile, tablet, and desktop layouts meet the three tested widths.
[ ] XLSX import is idempotent, path-safe, KaTeX-validated, and transactionally rolled back on error.
[ ] Publication requires all review flags, zero OCR issues, zero KaTeX errors, and a reviewer.
[ ] Production HTTPS, service restart, and daily backup are active.
```

- [ ] **Step 10: Commit deployment and final verification files**

```powershell
git add config/settings.py deploy
git commit -m "chore: add production deployment and backup"
git status --short
```

Expected: `git status --short` prints no uncommitted tracked changes.
