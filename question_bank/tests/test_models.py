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
