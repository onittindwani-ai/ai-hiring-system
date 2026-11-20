"""Tests for the Jev client, the fake Jev server and jev_check. No network beyond 127.0.0.1."""
import contextlib
import io
import json
import os
import sys
import threading
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hiring_fixtures  # noqa: F401,E402  (sets sys.path)
import jev  # noqa: E402
import jev_check  # noqa: E402
import mock_jev  # noqa: E402

NO_ENV = "/nonexistent/.env"
OK_BODY = {"model": "jev-test", "answers": {"q": {"type": "noul", "noul": 0.9}},
           "usage": {"input_tokens": 1000, "output_tokens": 5}}


def scripted_server(script):
    """A local server that answers with the next (code, body) of `script` for each request and records requests."""
    seen = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            seen.append({"path": self.path, "auth": self.headers.get("Authorization"),
                         "body": json.loads(self.rfile.read(length) or b"{}")})
            code, body = script[min(len(seen) - 1, len(script) - 1)]
            data = json.dumps(body).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, seen, "http://127.0.0.1:%d" % server.server_address[1]


class ClientTests(unittest.TestCase):
    def client(self, url, sleeps, **kwargs):
        return jev.JevClient(api_key="SECRET-KEY-123", base_url=url, env_file=NO_ENV, sleep=sleeps.append, **kwargs)

    def test_request_shape_and_answers(self):
        server, seen, url = scripted_server([(200, OK_BODY)])
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        answers, meta = self.client(url, []).ask("hello", {"q": jev.noul("Is it true")})
        self.assertEqual(answers["q"]["noul"], 0.9)
        self.assertEqual(meta["input_tokens"], 1000)
        self.assertEqual(seen[0]["path"], "/v1/systemone")
        self.assertEqual(seen[0]["auth"], "Bearer SECRET-KEY-123")
        self.assertEqual(set(seen[0]["body"]), {"state", "model", "questions"})
        self.assertEqual(seen[0]["body"]["model"], "jev-latest")

    def test_retries_on_429_then_works(self):
        server, seen, url = scripted_server([(429, {"error": "slow"}), (529, {"error": "busy"}), (200, OK_BODY)])
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        sleeps = []
        answers, _ = self.client(url, sleeps).ask("x", {"q": jev.noul("y")})
        self.assertIn("q", answers)
        self.assertEqual(len(seen), 3)
        self.assertEqual(sleeps, [1, 2])

    def test_gives_up_after_retries_with_plain_error(self):
        server, seen, url = scripted_server([(529, {"error": "busy"})])
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        sleeps = []
        with self.assertRaises(jev.JevError) as ctx:
            self.client(url, sleeps, max_retries=2).ask("x", {})
        self.assertEqual(len(seen), 3)
        self.assertEqual(sleeps, [1, 2])
        self.assertIn("529", str(ctx.exception))

    def test_401_is_not_retried_and_points_to_the_console(self):
        server, seen, url = scripted_server([(401, {"error": "bad key"})])
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        sleeps = []
        with self.assertRaises(jev.JevError) as ctx:
            self.client(url, sleeps).ask("x", {})
        self.assertEqual(len(seen), 1)
        self.assertEqual(sleeps, [])
        self.assertIn("console.typesafe.ai/keys", str(ctx.exception))

    def test_unreachable_server_is_plain(self):
        sleeps = []
        with self.assertRaises(jev.JevError) as ctx:
            self.client("http://127.0.0.1:9", sleeps, max_retries=1).ask("x", {})
        self.assertIn("Could not reach", str(ctx.exception))
        self.assertEqual(sleeps, [1])

    def test_key_never_appears_in_errors_or_repr(self):
        server, _, url = scripted_server([(500, {"error": "oops"})])
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        client = self.client(url, [])
        with self.assertRaises(jev.JevError) as ctx:
            client.ask("x", {})
        self.assertNotIn("SECRET-KEY-123", str(ctx.exception))
        self.assertNotIn("SECRET-KEY-123", repr(client))

    def test_missing_key_points_to_the_guide(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(jev.JevError) as ctx:
                jev.JevClient(env_file=NO_ENV)
        self.assertIn("docs/JEV-OPTIONAL.md", str(ctx.exception))

    def test_key_comes_from_environment_and_base_url_from_env(self):
        with mock.patch.dict(os.environ, {"TYPESAFE_API_KEY": "k", "JEV_BASE_URL": "http://127.0.0.1:1/"}, clear=True):
            client = jev.JevClient(env_file=NO_ENV)
        self.assertEqual(client.base_url, "http://127.0.0.1:1")

    def test_key_comes_from_a_local_env_file(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            env = Path(tmp) / ".env"
            env.write_text('# note\nTYPESAFE_API_KEY="from-file"\n', encoding="utf-8")
            with mock.patch.dict(os.environ, {}, clear=True):
                client = jev.JevClient(env_file=str(env))
                self.assertEqual(os.environ["TYPESAFE_API_KEY"], "from-file")
        self.assertIn("key=set", repr(client))

    def test_helpers_and_cost(self):
        self.assertEqual(jev.noul("a"), {"type": "noul", "instructions": "a"})
        self.assertEqual(jev.score("a", ["x", "y"])["criteria"], ["x", "y"])
        self.assertEqual(jev.choice("a", {"o": "d"})["criteria"], {"o": "d"})
        self.assertAlmostEqual(jev.estimate_cost(1_000_000), 0.042)
        self.assertEqual(jev.top_choice({"choice": "a", "probabilities": {"a": 0.7}, "confidence": 0.5}), ("a", 0.7, 0.5))
        self.assertIn("HTTP 422", jev.explain_http_error(422, "bad"))


class MockServerTests(unittest.TestCase):
    def setUp(self):
        self.server = mock_jev.start_server()
        self.addCleanup(mock_jev.stop_server, self.server)
        self.client = jev.JevClient(api_key="practice", base_url=mock_jev.server_url(self.server), env_file=NO_ENV)

    def questions(self):
        return {"s": jev.score("Rate ticket handling in a support queue. Evidence to look for: answered customer tickets",
                               ["0 none", "1 some", "2 more", "3 good", "4 great"]),
                "n": jev.noul("The person answered customer tickets in a support queue"),
                "c": jev.choice("Which team", {"billing": "payment invoices", "technical": "bugs errors"})}

    def test_same_shape_as_the_real_api(self):
        text = "I answered customer tickets in a busy support queue every day and handled many invoices and payments."
        answers, meta = self.client.ask(text, self.questions())
        self.assertEqual(set(answers), {"s", "n", "c"})
        self.assertIn(answers["s"]["score"], (0.0, 1.0, 2.0, 3.0, 4.0))
        self.assertTrue(0 <= answers["s"]["confidence"] <= 1)
        self.assertTrue(0 <= answers["n"]["noul"] <= 1)
        self.assertIn(answers["c"]["choice"], ("billing", "technical"))
        self.assertGreater(meta["input_tokens"], 0)
        self.assertIn("fake", meta["model"])

    def test_deterministic_and_responds_to_the_text(self):
        text = "I answered customer tickets in a busy support queue every day and handled many invoices and payments."
        a1, _ = self.client.ask(text, self.questions())
        a2, _ = self.client.ask(text, self.questions())
        self.assertEqual(a1, a2)
        empty, _ = self.client.ask("I stacked shelves in a grocery store for three years and enjoy cooking dinner.",
                                   self.questions())
        self.assertGreater(a1["s"]["score"], empty["s"]["score"])

    def test_rejects_calls_without_a_key_and_unknown_types(self):
        request = urllib.request.Request(mock_jev.server_url(self.server) + "/v1/systemone", data=b"{}", method="POST")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(request, timeout=5)
        self.assertEqual(ctx.exception.code, 401)
        with self.assertRaises(jev.JevError):
            self.client.ask("x", {"q": {"type": "other", "instructions": "x"}})

    def test_says_it_is_fake(self):
        self.assertIn("FAKE Jev for practice, not the real model", mock_jev.BANNER)


class JevCheckTests(unittest.TestCase):
    def test_mock_flag_works_offline(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = jev_check.main(["--mock"])
        self.assertEqual(code, 0)
        self.assertIn("FAKE Jev", out.getvalue())
        self.assertIn("estimated cost", out.getvalue())

    def test_missing_key_message(self):
        out = io.StringIO()
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(jev.hlib, "load_env_file", lambda *a, **k: None):
            with contextlib.redirect_stdout(out):
                code = jev_check.main([])
        self.assertEqual(code, 1)
        self.assertIn("docs/JEV-OPTIONAL.md", out.getvalue())


if __name__ == "__main__":
    unittest.main()
