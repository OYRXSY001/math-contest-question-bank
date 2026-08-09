import tempfile
from pathlib import Path

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import RequestFactory, TestCase, override_settings
from django.utils import timezone

from question_bank.admin import QuestionAdmin, QuestionKnowledgeInline
from question_bank.models import KnowledgePoint, Paper, Question, QuestionKnowledgePoint


class MessageCollector:
    def __init__(self):
        self.messages = []

    def add(self, level, message, extra_tags=""):
        self.messages.append(message)


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
        request = self.publish_request()

        self.model_admin.publish_reviewed(
            request, Question.objects.filter(pk=self.question.pk)
        )

        self.question.refresh_from_db()
        self.assertEqual(self.question.status, Question.Status.DRAFT)

    def publish_request(self):
        request = RequestFactory().post("/admin/")
        request.user = self.staff
        request._messages = MessageCollector()
        return request

    def mark_reviewed(self, question, **overrides):
        values = {
            "text_checked": True,
            "formula_checked": True,
            "solution_checked": True,
            "reviewed_by": self.staff,
            "reviewed_at": timezone.now(),
            "status": Question.Status.REVIEWED,
        }
        values.update(overrides)
        for field, value in values.items():
            setattr(question, field, value)
        question.save()

    def publish_with_primary_knowledge(self):
        self.mark_reviewed(self.question)
        knowledge = KnowledgePoint.objects.create(
            name="Primary knowledge", slug="primary-knowledge", subject="calculus"
        )
        relation = QuestionKnowledgePoint.objects.create(
            question=self.question, knowledge_point=knowledge, is_primary=True
        )
        self.question.status = Question.Status.PUBLISHED
        self.question.save()
        return relation

    def inline_formset(self, rows, initial_forms=1):
        inline = QuestionKnowledgeInline(Question, admin.site)
        formset_class = inline.get_formset(self.publish_request(), self.question)
        prefix = formset_class.get_default_prefix()
        data = {
            f"{prefix}-TOTAL_FORMS": str(len(rows)),
            f"{prefix}-INITIAL_FORMS": str(initial_forms),
            f"{prefix}-MIN_NUM_FORMS": "0",
            f"{prefix}-MAX_NUM_FORMS": "1000",
        }
        for index, row in enumerate(rows):
            for field, value in row.items():
                data[f"{prefix}-{index}-{field}"] = value
        return formset_class(data=data, instance=self.question)

    def test_published_question_cannot_delete_its_only_primary_inline(self):
        relation = self.publish_with_primary_knowledge()
        formset = self.inline_formset(
            [
                {
                    "id": str(relation.pk),
                    "knowledge_point": str(relation.knowledge_point_id),
                    "is_primary": "on",
                    "DELETE": "on",
                }
            ]
        )

        self.assertFalse(formset.is_valid())
        self.assertIn(
            "exactly one primary knowledge point", str(formset.non_form_errors())
        )

    def test_published_question_can_replace_primary_inline(self):
        relation = self.publish_with_primary_knowledge()
        replacement = KnowledgePoint.objects.create(
            name="Replacement knowledge",
            slug="replacement-knowledge",
            subject="calculus",
        )
        formset = self.inline_formset(
            [
                {
                    "id": str(relation.pk),
                    "knowledge_point": str(relation.knowledge_point_id),
                    "is_primary": "on",
                    "DELETE": "on",
                },
                {
                    "knowledge_point": str(replacement.pk),
                    "is_primary": "on",
                },
            ]
        )

        self.assertTrue(formset.is_valid(), formset.errors)
        formset.save()
        self.assertEqual(
            list(
                self.question.questionknowledgepoint_set.filter(
                    is_primary=True
                ).values_list("knowledge_point_id", flat=True)
            ),
            [replacement.pk],
        )

    def test_publish_action_skips_question_without_review_time(self):
        self.mark_reviewed(self.question, reviewed_at=None)
        knowledge = KnowledgePoint.objects.create(
            name="函数极限", slug="function-limit", subject="calculus"
        )
        QuestionKnowledgePoint.objects.create(
            question=self.question, knowledge_point=knowledge, is_primary=True
        )

        self.model_admin.publish_reviewed(
            self.publish_request(), Question.objects.filter(pk=self.question.pk)
        )

        self.question.refresh_from_db()
        self.assertEqual(self.question.status, Question.Status.REVIEWED)

    def test_publish_action_skips_question_without_primary_knowledge_point(self):
        self.mark_reviewed(self.question)

        self.model_admin.publish_reviewed(
            self.publish_request(), Question.objects.filter(pk=self.question.pk)
        )

        self.question.refresh_from_db()
        self.assertEqual(self.question.status, Question.Status.REVIEWED)

    def test_publish_action_publishes_eligible_reviewed_question(self):
        self.mark_reviewed(self.question)
        knowledge = KnowledgePoint.objects.create(
            name="函数极限", slug="function-limit", subject="calculus"
        )
        QuestionKnowledgePoint.objects.create(
            question=self.question, knowledge_point=knowledge, is_primary=True
        )

        request = self.publish_request()
        self.model_admin.publish_reviewed(
            request, Question.objects.filter(pk=self.question.pk)
        )

        self.question.refresh_from_db()
        self.assertEqual(self.question.status, Question.Status.PUBLISHED)
        self.assertEqual(request._messages.messages, ["已发布 1 题，跳过 0 题。"])

    def test_publish_action_skips_already_published_question(self):
        self.mark_reviewed(self.question)
        knowledge = KnowledgePoint.objects.create(
            name="函数极限", slug="function-limit", subject="calculus"
        )
        QuestionKnowledgePoint.objects.create(
            question=self.question, knowledge_point=knowledge, is_primary=True
        )
        self.question.status = Question.Status.PUBLISHED
        self.question.save()

        request = self.publish_request()
        self.model_admin.publish_reviewed(
            request, Question.objects.filter(pk=self.question.pk)
        )

        self.question.refresh_from_db()
        self.assertEqual(self.question.status, Question.Status.PUBLISHED)
        self.assertEqual(request._messages.messages, ["已发布 0 题，跳过 1 题。"])
