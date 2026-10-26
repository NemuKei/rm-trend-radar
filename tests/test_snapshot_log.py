from copy import deepcopy
from datetime import UTC, datetime
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from rm_trend_radar.snapshot_log import (
    LOG_PREFIX, MAX_ARTICLES, MAX_INPUT_BYTES, MAX_LOG_BYTES,
    emit_snapshot_log, render_snapshot_log,
)

RUN = {"run_id": "123456789", "run_attempt": "1", "head_sha": "a" * 40}


def article(**changes):
    row = {"source_name": "IDeaS", "title_en": "Pricing without unnecessary discounts",
           "url": "https://ideas.com/pricing-without-discounts/", "published_date": "2026-10-25",
           "tags": ["unreviewed"], "review_status": "unreviewed", "public_candidate": False}
    row.update(changes)
    return row


def snapshot(*rows):
    return {"contract": "rss-metadata-only-v1", "generated_at_utc": "2026-10-26T00:01:02+00:00",
            "lp_ready": False, "publish_decision": "manual_review_required",
            "sources": [{"source": "IDeaS", "fetched": len(rows), "failed": 0, "error": None},
                        {"source": "SiteMinder", "fetched": 0, "failed": 1,
                         "error": "Authorization: Bearer PRIVATE_ERROR_VALUE"}],
            "articles": list(rows)}


def records(text):
    return [json.loads(line.removeprefix(LOG_PREFIX)) for line in text.splitlines()]


class SnapshotLogTest(unittest.TestCase):
    def test_metadata_counts_identity_partial_failure_and_checksum(self):
        value = snapshot(article())
        before = deepcopy(value)
        text = render_snapshot_log(value, **RUN)
        data = records(text)
        self.assertEqual(value, before)
        self.assertEqual(data[0]["run_id"], RUN["run_id"])
        self.assertEqual(data[0]["head_sha"], RUN["head_sha"])
        self.assertEqual(datetime.fromisoformat(data[0]["generated_at_utc"]).tzinfo, UTC)
        self.assertEqual(data[0]["article_count"], 1)
        self.assertFalse(data[0]["lp_ready"])
        self.assertEqual(data[2], {"kind": "source", "source": "SiteMinder", "fetched": 0, "failed": 1})
        self.assertEqual(set(data[3]), {"kind", "source_name", "title_en", "url", "published_date"})
        self.assertEqual(data[-1]["emitted_count"], 1)
        self.assertTrue(data[-1]["complete"])
        payload = "\n".join(line.removeprefix(LOG_PREFIX) for line in text.splitlines()[:-1]) + "\n"
        self.assertEqual(data[-1]["sha256"], hashlib.sha256(payload.encode("ascii")).hexdigest())
        self.assertNotIn("PRIVATE_ERROR_VALUE", text)

    def test_never_logs_extra_fields_or_body(self):
        value = snapshot(article(description="PRIVATE_BODY", **{"content:encoded": "PRIVATE_BODY"},
                                 note="PRIVATE_NOTE", author="PRIVATE_AUTHOR", tags=["PRIVATE_TAG"]))
        value["private"] = "PRIVATE_TOP_LEVEL"
        text = render_snapshot_log(value, **RUN)
        self.assertNotIn("PRIVATE_", text)

    def test_actions_commands_are_escaped_but_round_trip(self):
        title = "::error::pwn ##[warning]bad ::stop-commands::x"
        text = render_snapshot_log(snapshot(article(title_en=title)), **RUN)
        self.assertNotIn("::", text)
        self.assertNotIn("##[", text)
        self.assertEqual(records(text)[3]["title_en"], title)

    def test_unsafe_titles_are_held_without_echo(self):
        for title in ["x\n::error::pwn", "x\rforge", "x\x1b[31m", "x\u202eevil", "<p>Body</p>",
                      "Contact guest@example.com", "Call +81 90 1234 5678", "password=private",
                      "Bearer private", "api_key: private", "github_pat_private", "a" * 241,
                      "token=example-token-value", "Cookie: session-value", "auth=example-value",
                      "Read https://example.com/?token=private", "Token " + "aB012345" * 5]:
            with self.subTest(title_kind=title[:10]):
                data = records(render_snapshot_log(snapshot(article(title_en=title)), **RUN))
                self.assertEqual(data[-1]["emitted_count"], 0)
                self.assertEqual(data[-1]["omitted_count"], 1)
                self.assertFalse(data[-1]["complete"])

    def test_unsafe_urls_are_held_without_echo(self):
        for url in ["http://ideas.com/post/", "https://ideas.com/post/?token=PRIVATE_URL",
                    "https://ideas.com/post/#PRIVATE_URL", "https://user:PRIVATE_URL@ideas.com/post/",
                    "https://ideas.com:443/post/", "https://evil.example/post/",
                    "https://ideas.com.evil.example/post/", "https://ideas.com/guest%40example.com/",
                    "https://ideas.com/phone-09012345678/", "https://ideas.com/secret/PRIVATE_URL/",
                    "https://ideas.com/token/PRIVATE_URL/", "https://ideas.com/api/key/PRIVATE_URL/",
                    "https://ideas.com/XhKpq-9VNrx2-UzFG5Ds-TwBH7Qp-MvaY4jL-cE6R8uZ/",
                    "https://ideas.com/xhkpq-9vnrx2-uzfg5ds-twbh7qp-mvay4jl-ce6r8uz/",
                    "https://ideas.com/b2b-sales/", "https://ideas.com/hotel_pricing/",
                    "https://ideas.com/post-12345/",
                    "https://ideas.com/" + "aB012345" * 5 + "/", "https://ideas.com/\nprivate/",
                    "https://ideas.com/" + "word-" * 110]:
            with self.subTest(url_kind=url[:30]):
                text = render_snapshot_log(snapshot(article(url=url)), **RUN)
                self.assertNotIn("PRIVATE_URL", text)
                self.assertEqual(records(text)[-1]["emitted_count"], 0)

    def test_normal_long_public_slugs_and_calendar_paths_are_retained(self):
        rows = [article(url="https://ideas.com/2026/10/a-booking-gap-is-not-a-demand-diagnosis-four-checks-before-you-discount/"),
                article(url="https://ideas.com/5-ways-to-improve-hotel-revenue-management/")]
        end = records(render_snapshot_log(snapshot(*rows), **RUN))[-1]
        self.assertTrue(end["complete"])
        self.assertEqual(end["emitted_count"], 2)

    def test_valid_dates_and_unique_urls_required(self):
        value = snapshot(article(), article(), article(published_date="2026-02-30"))
        end = records(render_snapshot_log(value, **RUN))[-1]
        self.assertEqual(end["emitted_count"], 1)
        self.assertEqual(end["omitted_reasons"], {"duplicate_url": 1, "invalid_date": 1})

    def test_article_and_byte_limits_are_visible(self):
        rows = [article(url=f"https://ideas.com/hotel-{i}/") for i in range(MAX_ARTICLES + 5)]
        text = render_snapshot_log(snapshot(*rows), **RUN)
        end = records(text)[-1]
        self.assertEqual(end["emitted_count"], MAX_ARTICLES)
        self.assertEqual(end["omitted_reasons"], {"article_limit": 5})
        self.assertLessEqual(len(text.encode()), MAX_LOG_BYTES)
        rows = [article(url=f"https://ideas.com/hotel-{i}/", title_en="宿" * 240) for i in range(MAX_ARTICLES)]
        text = render_snapshot_log(snapshot(*rows), **RUN)
        self.assertLessEqual(len(text.encode()), MAX_LOG_BYTES)
        self.assertGreater(records(text)[-1]["omitted_reasons"]["byte_limit"], 0)

    def test_invalid_envelopes_fail_closed(self):
        cases = []
        for key, value in [("lp_ready", True), ("generated_at_utc", "2026-10-26T00:01:02"),
                           ("generated_at_utc", "2026-10-26T09:01:02+09:00"), ("sources", []),
                           ("contract", "unknown")]:
            case = snapshot(article()); case[key] = value; cases.append(case)
        case = snapshot(article()); case["sources"][0]["fetched"] = 2; cases.append(case)
        case = snapshot(article()); case["sources"][0]["fetched"] = True; cases.append(case)
        case = snapshot(article()); case["articles"][0]["source_name"] = "unknown"; cases.append(case)
        for case in cases:
            with self.subTest(case_type=list(case)):
                with self.assertRaises(ValueError):
                    render_snapshot_log(case, **RUN)

    def test_file_boundary_has_static_errors_and_preserves_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            for raw in [b'{"PRIVATE_BROKEN_JSON', b"x" * (MAX_INPUT_BYTES + 1), b"null",
                        b"[" * 10000 + b"0" + b"]" * 10000]:
                path.write_bytes(raw)
                output = io.StringIO()
                self.assertEqual(emit_snapshot_log(path, stream=output, **RUN), 1)
                self.assertEqual(records(output.getvalue()), [{"kind": "error", "reason": "invalid_snapshot_or_run"}])
                self.assertEqual(path.read_bytes(), raw)
            raw = json.dumps(snapshot(article())).encode()
            path.write_bytes(raw)
            output = io.StringIO()
            self.assertEqual(emit_snapshot_log(path, stream=output, **RUN), 0)
            self.assertTrue(records(output.getvalue())[-1]["complete"])
            self.assertEqual(path.read_bytes(), raw)
            output = io.StringIO()
            self.assertEqual(emit_snapshot_log(path, stream=output, **{**RUN, "run_id": "PRIVATE_BAD_ID"}), 1)
            self.assertNotIn("PRIVATE_BAD_ID", output.getvalue())


if __name__ == "__main__":
    unittest.main()
