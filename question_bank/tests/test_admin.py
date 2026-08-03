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
