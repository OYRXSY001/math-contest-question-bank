from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
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
            original_category_label="非数学A类",
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

    def test_paper_detail_with_uploaded_pdf_renders_before_download_route_exists(self):
        upload = SimpleUploadedFile(
            "paper.pdf", b"%PDF-1.4\n%%EOF\n", content_type="application/pdf"
        )
        self.paper.pdf_file.save(upload.name, upload, save=True)
        self.addCleanup(self.paper.pdf_file.delete, save=False)
        self.client.raise_request_exception = False

        response = self.client.get(reverse("paper-detail", args=[self.paper.pk]))

        self.assertEqual(response.status_code, 200)

    def test_markdown_escapes_raw_html_and_keeps_latex(self):
        rendered = str(render_markdown(r"<script>alert(1)</script> \(x^2\)"))

        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn(r"\(x^2\)", rendered)

    def test_markdown_drops_dangerous_link_and_image_uris(self):
        rendered = str(
            render_markdown(
                "[script](javascript:alert(1)) "
                "![data](data:text/html;base64,PHNjcmlwdD4=) "
                "[obfuscated](java&#x09;script:alert(1))"
            )
        )

        self.assertNotIn("href=\"javascript:", rendered.lower())
        self.assertNotIn("href=\"java&#x09;script:", rendered.lower())
        self.assertNotIn("src=\"data:", rendered.lower())

    def test_markdown_drops_newline_obfuscated_link_and_image_uris(self):
        rendered = str(
            render_markdown(
                "[line-feed](java\nscript:alert(1)) "
                "![line-feed](java\nscript:alert(1)) "
                "[carriage-return](java\rscript:alert(1)) "
                "![carriage-return](java\rscript:alert(1))"
            )
        )

        self.assertNotRegex(rendered.lower(), r"""(?:href|src)="[^"]*java[\r\n]script:""")

    def test_markdown_keeps_safe_link_uris(self):
        rendered = str(
            render_markdown(
                "[relative](/papers/) [https](https://example.com/) "
                "[email](mailto:study@example.com) ![image](/image.png)"
            )
        )

        self.assertIn('href="/papers/"', rendered)
        self.assertIn('href="https://example.com/"', rendered)
        self.assertIn('href="mailto:study@example.com"', rendered)
        self.assertIn('src="/image.png"', rendered)

    def test_markdown_preserves_private_use_characters_and_latex(self):
        source = "\ue000 \ue001 \ue002 \ue003 \\(x^2\\)"

        rendered = str(render_markdown(source))

        self.assertIn("\ue000 \ue001 \ue002 \ue003", rendered)
        self.assertIn(r"\(x^2\)", rendered)
