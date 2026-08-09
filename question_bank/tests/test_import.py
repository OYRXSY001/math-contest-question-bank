import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from openpyxl import Workbook

from question_bank.katex import extract_formulas, validate_markdown_formulas
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

    def assert_question_is_rejected(self, question_row, reason):
        inventory_rows, question_rows = self.valid_rows()
        question_rows[0] = question_row
        inventory = self.root / "inventory.xlsx"
        questions = self.root / "questions.xlsx"
        self.write_workbook(inventory, INVENTORY_HEADERS, inventory_rows)
        self.write_workbook(questions, QUESTION_HEADERS, question_rows)

        with self.assertRaisesMessage(CommandError, "questions 第2行") as error:
            call_command(
                "import_question_bank",
                inventory=str(inventory),
                questions=str(questions),
            )

        self.assertIn(reason, str(error.exception))
        self.assertFalse(Paper.objects.exists())
        self.assertFalse(Question.objects.exists())

    def test_blank_ocr_confidence_is_rejected(self):
        _, question_rows = self.valid_rows()
        question = question_rows[0].copy()
        question[14] = ""

        self.assert_question_is_rejected(
            question, "ocr_confidence: 必须是 0 到 1 之间的数字"
        )

    def test_out_of_range_ocr_confidence_is_rejected(self):
        _, question_rows = self.valid_rows()

        for confidence in (-0.01, 1.01):
            with self.subTest(confidence=confidence):
                question = question_rows[0].copy()
                question[14] = confidence
                self.assert_question_is_rejected(
                    question, "ocr_confidence: 必须在 0 到 1 之间"
                )

    def test_low_ocr_confidence_without_ocr_items_is_rejected(self):
        _, question_rows = self.valid_rows()
        question = question_rows[0].copy()
        question[14] = 0.89
        question[15] = False
        question[18] = 0

        self.assert_question_is_rejected(
            question,
            "OCR 置信度低于 0.90 时必须登记 unresolved_ocr_items",
        )

    def test_low_ocr_confidence_with_checked_text_is_accepted(self):
        inventory_rows, question_rows = self.valid_rows()
        question_rows[0][14] = 0.89
        question_rows[0][15] = True
        question_rows[0][18] = 0
        inventory = self.root / "inventory.xlsx"
        questions = self.root / "questions.xlsx"
        self.write_workbook(inventory, INVENTORY_HEADERS, inventory_rows)
        self.write_workbook(questions, QUESTION_HEADERS, question_rows)

        call_command(
            "import_question_bank", inventory=str(inventory), questions=str(questions)
        )

        self.assertTrue(Question.objects.exists())

    def test_unicode_replacement_character_in_stem_is_rejected(self):
        _, question_rows = self.valid_rows()
        question = question_rows[0].copy()
        question[8] = "损坏的题干 �"

        self.assert_question_is_rejected(
            question, "stem_md: 包含Unicode 替换字符 �"
        )

    def test_empty_box_in_solution_is_rejected(self):
        _, question_rows = self.valid_rows()
        question = question_rows[0].copy()
        question[10] = "损坏的解答 □"

        self.assert_question_is_rejected(question, "solution_md: 包含空方框 □")

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

    def test_fractional_integer_is_rejected(self):
        inventory_rows, question_rows = self.valid_rows()
        inventory_rows[0][0] = 17.5
        inventory = self.root / "inventory.xlsx"
        questions = self.root / "questions.xlsx"
        self.write_workbook(inventory, INVENTORY_HEADERS, inventory_rows)
        self.write_workbook(questions, QUESTION_HEADERS, question_rows)

        with self.assertRaises(CommandError):
            call_command("import_question_bank", inventory=str(inventory), questions=str(questions))

        self.assertFalse(Paper.objects.exists())

    def test_boolean_integer_is_rejected(self):
        inventory_rows, question_rows = self.valid_rows()
        question_rows[0][3] = True
        inventory = self.root / "inventory.xlsx"
        questions = self.root / "questions.xlsx"
        self.write_workbook(inventory, INVENTORY_HEADERS, inventory_rows)
        self.write_workbook(questions, QUESTION_HEADERS, question_rows)

        with self.assertRaises(CommandError):
            call_command("import_question_bank", inventory=str(inventory), questions=str(questions))

        self.assertFalse(Paper.objects.exists())

    def test_fractional_exam_year_is_rejected(self):
        inventory_rows, question_rows = self.valid_rows()
        inventory_rows[0][4] = 2025.5
        inventory = self.root / "inventory.xlsx"
        questions = self.root / "questions.xlsx"
        self.write_workbook(inventory, INVENTORY_HEADERS, inventory_rows)
        self.write_workbook(questions, QUESTION_HEADERS, question_rows)

        with self.assertRaises(CommandError):
            call_command("import_question_bank", inventory=str(inventory), questions=str(questions))

        self.assertFalse(Paper.objects.exists())

    def test_unknown_boolean_is_rejected(self):
        inventory_rows, question_rows = self.valid_rows()
        question_rows[0][15] = "checked"
        inventory = self.root / "inventory.xlsx"
        questions = self.root / "questions.xlsx"
        self.write_workbook(inventory, INVENTORY_HEADERS, inventory_rows)
        self.write_workbook(questions, QUESTION_HEADERS, question_rows)

        with self.assertRaises(CommandError):
            call_command("import_question_bank", inventory=str(inventory), questions=str(questions))

        self.assertFalse(Paper.objects.exists())

    def test_explicit_boolean_vocabulary_is_accepted(self):
        inventory_rows, question_rows = self.valid_rows()
        question_rows[0][15:18] = ["yes", 0, "否"]
        inventory = self.root / "inventory.xlsx"
        questions = self.root / "questions.xlsx"
        self.write_workbook(inventory, INVENTORY_HEADERS, inventory_rows)
        self.write_workbook(questions, QUESTION_HEADERS, question_rows)

        try:
            call_command("import_question_bank", inventory=str(inventory), questions=str(questions))
        except CommandError as error:
            self.fail(f"explicit boolean vocabulary was rejected: {error}")

        self.assertEqual(Question.objects.get().status, "draft")

    def test_formula_delimiters_are_scanned_in_order(self):
        invalid = [
            r"\)broken\(",
            r"\(broken",
            r"broken\)",
            r"\(crossed \[formula\)\]",
        ]

        for text in invalid:
            with self.subTest(text=text):
                self.assertTrue(validate_markdown_formulas([("stem", text)]))

        self.assertEqual(
            extract_formulas(r"\(x+1\) and \[y^2\]"),
            ["x+1", "y^2"],
        )

    def test_reversed_formula_delimiters_roll_back_whole_import(self):
        inventory_rows, question_rows = self.valid_rows()
        question_rows[0][8] = r"错误定界符 \)broken\("
        inventory = self.root / "inventory.xlsx"
        questions = self.root / "questions.xlsx"
        self.write_workbook(inventory, INVENTORY_HEADERS, inventory_rows)
        self.write_workbook(questions, QUESTION_HEADERS, question_rows)

        with self.assertRaises(CommandError):
            call_command("import_question_bank", inventory=str(inventory), questions=str(questions))

        self.assertFalse(Paper.objects.exists())

    def test_duplicate_secondary_knowledge_is_rejected_before_writes(self):
        KnowledgePoint.objects.create(
            name="导数", slug="derivative", subject="calculus"
        )
        inventory_rows, question_rows = self.valid_rows()
        question_rows[0][7] = "derivative,derivative"
        inventory = self.root / "inventory.xlsx"
        questions = self.root / "questions.xlsx"
        self.write_workbook(inventory, INVENTORY_HEADERS, inventory_rows)
        self.write_workbook(questions, QUESTION_HEADERS, question_rows)

        try:
            call_command("import_question_bank", inventory=str(inventory), questions=str(questions))
        except CommandError:
            pass
        except Exception as error:
            self.fail(f"expected CommandError, got {type(error).__name__}: {error}")
        else:
            self.fail("CommandError not raised")

        self.assertFalse(Paper.objects.exists())
