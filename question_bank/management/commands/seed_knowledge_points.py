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
