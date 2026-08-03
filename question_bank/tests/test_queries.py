from django.contrib.auth import get_user_model
from django.http import QueryDict
from django.test import TestCase

from question_bank.models import (
    Favorite,
    KnowledgePoint,
    Paper,
    Question,
    QuestionKnowledgePoint,
    WrongQuestion,
)
from question_bank.queries import filtered_questions, with_user_flags


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

    def test_with_user_flags_marks_only_the_users_records(self):
        Favorite.objects.create(user=self.reviewer, question=self.q_limit)
        WrongQuestion.objects.create(user=self.reviewer, question=self.q_continuity)

        questions = with_user_flags(Question.objects.order_by("id"), self.reviewer)
        flags = {question.id: (question.is_favorite, question.is_wrong) for question in questions}

        self.assertEqual(flags[self.q_limit.id], (True, False))
        self.assertEqual(flags[self.q_continuity.id], (False, True))
        self.assertEqual(flags[self.q_final.id], (False, False))
