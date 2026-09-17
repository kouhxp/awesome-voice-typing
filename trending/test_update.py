import io
import json
import unittest
from datetime import date, datetime, timezone
from unittest.mock import call, patch

import update


TODAY = date(2026, 9, 17)
README = f"""# Tools
| [Badge](https://github.com/outside/badge) |
## Trending Voice Typing Tools
{update.START}

Existing table

{update.END}

## Directory
| Tool | Description |
| --- | --- |
| [Alpha](https://github.com/owner/alpha/) | First |
| [Duplicate](https://github.com/OWNER/ALPHA) | Duplicate |
| [Nested](https://github.com/owner/nested/tree/main) | Skip |
| [Beta](https://github.com/owner/beta) | Second |
## Other
| [Other](https://github.com/outside/other) |
"""


def response(data):
    return io.BytesIO(json.dumps(data).encode())


class UpdateTests(unittest.TestCase):
    def test_discover_only_directory_root_links(self):
        self.assertEqual(
            update.discover(README),
            [("Alpha", "owner/alpha"), ("Beta", "owner/beta")],
        )

    def test_calculate_includes_first_day_and_yesterday_only(self):
        history = [
            {
                "week": int(datetime(2026, 8, 17, tzinfo=timezone.utc).timestamp()),
                "days": [100, 1, 2, 3, 4, 5, 6],
            },
            {
                "week": int(datetime(2026, 9, 14, tzinfo=timezone.utc).timestamp()),
                "days": [7, 8, 9, 100, 100, 100, 100],
            },
        ]
        self.assertEqual(update.calculate(history, TODAY), 45)

    def test_render_order_limit_growth_and_date(self):
        rows = [
            ("Beta", "owner/beta", 10, 10),
            ("Zero", "owner/zero", 0, 100),
            ("alpha", "owner/alpha", 10, 5),
            ("Leader", "owner/leader", 1234, 3702),
        ]
        with patch.object(update, "TOP_N", 3):
            rendered = update.render(rows, TODAY)
            self.assertEqual(rendered, update.render(rows, TODAY))
        self.assertEqual(
            rendered,
            "Based on stars gained in the last 30 days | Last updated: 2026-09-17\n"
            "\n"
            "| Tool | Stars gained (30 days) | Total stars | Growth |\n"
            "| --- | ---: | ---: | ---: |\n"
            "| [Leader](https://github.com/owner/leader) | 1,234 | 3,702 | 50.0% |\n"
            "| [alpha](https://github.com/owner/alpha) | 10 | 5 | — |\n"
            "| [Beta](https://github.com/owner/beta) | 10 | 10 | — |",
        )

    def test_replace_preserves_surroundings_and_is_repeatable(self):
        updated = update.replace_block(README, "New table")
        self.assertEqual(updated, README.replace("Existing table", "New table"))
        self.assertEqual(update.replace_block(updated, "New table"), updated)

    def test_fetch_retries_then_returns_json(self):
        with (
            patch.object(update, "urlopen", side_effect=[
                OSError("temporary"), OSError("temporary"), response({"count": 12}),
            ]) as request,
            patch.object(update.time, "sleep") as sleep,
            patch("builtins.print"),
        ):
            self.assertEqual(update.fetch("owner/repo", "count", "token"), {"count": 12})
        self.assertEqual(request.call_count, 3)
        self.assertEqual(sleep.call_args_list, [call(2), call(2)])
        args, kwargs = request.call_args
        self.assertEqual(args[0].full_url, "https://api.github.com/repos/owner/repo/stargazers/count")
        self.assertEqual(args[0].get_header("Authorization"), "Bearer token")
        self.assertEqual(kwargs, {"timeout": 20})

    def test_main_skips_repository_if_either_endpoint_fails(self):
        for endpoint in ("history", "count"):
            with self.subTest(endpoint=endpoint):
                replies = ([response([])] if endpoint == "count" else [])
                replies += [OSError("unavailable")] * 3
                replies += [response([]), response({"count": 100})]
                with (
                    patch.dict(update.os.environ, {"GITHUB_TOKEN": "token"}),
                    patch.object(update, "README") as readme,
                    patch.object(update, "datetime") as clock,
                    patch.object(update, "urlopen", side_effect=replies),
                    patch.object(update.time, "sleep"),
                    patch("builtins.print"),
                ):
                    readme.read_text.return_value = README
                    clock.now.return_value.date.return_value = TODAY
                    update.main()
                expected = update.replace_block(
                    README, update.render([("Beta", "owner/beta", 0, 100)], TODAY),
                )
                readme.write_text.assert_called_once_with(expected, encoding="utf-8")
                clock.now.assert_called_once_with(timezone.utc)

    def test_main_preserves_readme_when_all_requests_fail(self):
        with (
            patch.dict(update.os.environ, {"GITHUB_TOKEN": "token"}),
            patch.object(update, "README") as readme,
            patch.object(update, "urlopen", side_effect=OSError("unavailable")) as request,
            patch.object(update.time, "sleep"),
            patch("builtins.print"),
        ):
            readme.read_text.return_value = README
            update.main()
        self.assertEqual(request.call_count, 6)
        readme.write_text.assert_not_called()


if __name__ == "__main__":
    unittest.main()
