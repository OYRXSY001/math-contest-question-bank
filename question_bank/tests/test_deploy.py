import re
from pathlib import Path

from django.test import SimpleTestCase


class CaddyConfigurationTests(SimpleTestCase):
    def test_only_question_media_is_served_directly(self):
        config = (
            Path(__file__).resolve().parents[2] / "deploy" / "Caddyfile"
        ).read_text(encoding="utf-8")
        file_server_routes = dict(
            re.findall(
                r"handle_path\s+(\S+)\s+\{\s*root\s+\*\s+(\S+)\s+file_server\s+\}",
                config,
                re.MULTILINE,
            )
        )

        self.assertEqual(
            file_server_routes.get("/media/questions/*"),
            "/srv/cmc-a/media/questions",
        )
        self.assertNotIn("/media/*", file_server_routes)
