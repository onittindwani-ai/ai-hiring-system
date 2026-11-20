"""FAKE Jev for practice. This is NOT the real model (Python 3.9+, standard library only).

Usage:
    python3 tools/mock_jev.py            # serves on http://127.0.0.1:8765
    python3 tools/mock_jev.py 9000       # another port
    JEV_BASE_URL=http://127.0.0.1:8765 TYPESAFE_API_KEY=practice python3 tools/jev_check.py

What it does:
    Answers the same request shape as the real API (`model`, `answers`, `usage`) so you can try the
    whole scoring flow offline, with no key and no cost. Its answers are simple word overlap guesses
    between the question and the text, the same every time. Never use its results to judge a person.
"""
import json
import re
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BANNER = "FAKE Jev for practice, not the real model"
STOP = set("""about above after again also another because been before being between both could does done each
from have here into just like more most much must only other over same should some such than that their them
then there these they this those through under very want were what when where which while with without would
your rate strongly text shows show real examples example evidence look looks needed candidate resume person
how for and the are was has had its not you who can will""".split())


def stems(text):
    """Set of word stems (first 5 letters) for words of 4 or more letters, minus common words."""
    return {w[:5] for w in re.findall(r"[a-z]{4,}", str(text).lower()) if w not in STOP}


def answer_score(state_stems, question):
    levels = question.get("criteria", [])
    top = max(len(levels) - 1, 1)
    hits = len(state_stems & stems(question.get("instructions", "")))
    index = 0 if hits == 0 else 1 if hits <= 1 else 2 if hits <= 3 else 3 if hits <= 5 else 4
    index = min(index, top)
    confidence = 0.6 if hits == 0 else min(0.9, 0.5 + 0.08 * min(hits, 5))
    if len(state_stems) < 25:
        confidence = min(confidence, 0.5)  # very short text: less sure
    spread = round(0.4 / max(1, len(levels) - 1), 3)
    probs = {str(i): (0.6 if i == index else spread) for i in range(len(levels))}
    return {"type": "score", "score": float(index), "confidence": round(confidence, 2),
            "legend": {str(i): d for i, d in enumerate(levels)}, "probabilities": probs}


def answer_noul(state_stems, question):
    statement = stems(question.get("instructions", ""))
    ratio = len(state_stems & statement) / max(1, len(statement))
    return {"type": "noul", "noul": round(min(0.95, 0.05 + 0.9 * ratio), 2)}


def answer_choice(state_stems, question):
    options = question.get("criteria", {})
    raw = {name: len(state_stems & stems(name.replace("_", " ") + " " + str(desc))) + 0.1
           for name, desc in options.items()}
    total = sum(raw.values()) or 1.0
    probs = {k: round(v / total, 2) for k, v in raw.items()}
    best = max(probs, key=probs.get) if probs else None
    ordered = sorted(probs.values(), reverse=True)
    margin = (ordered[0] - (ordered[1] if len(ordered) > 1 else 0)) if ordered else 0
    return {"type": "choice", "choice": best, "confidence": round(min(1.0, 0.4 + margin), 2),
            "probabilities": probs}


ANSWERERS = {"score": answer_score, "noul": answer_noul, "choice": answer_choice}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/v1/systemone":
            return self.reply(404, {"error": "not found"})
        if not self.headers.get("Authorization", "").startswith("Bearer "):
            return self.reply(401, {"error": "missing key"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except ValueError:
            return self.reply(422, {"error": "body is not JSON"})
        state = str(body.get("state", ""))
        state_stems = stems(state)
        answers = {}
        for name, question in (body.get("questions") or {}).items():
            fn = ANSWERERS.get(question.get("type"))
            if fn is None:
                return self.reply(422, {"error": "unknown question type %s" % question.get("type")})
            answers[name] = fn(state_stems, question)
        tokens = max(1, len(state) // 4 + 60 * len(answers))
        self.reply(200, {"model": "fake-jev-for-practice", "answers": answers,
                         "usage": {"input_tokens": tokens, "output_tokens": 10}})

    def reply(self, code, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Fake-Jev", "true")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


def start_server(port=0, host="127.0.0.1"):
    """Start the fake server in a background thread. Port 0 picks a free port.
    Returns the server; its URL is http://127.0.0.1:<server.server_address[1]>. Stop with stop_server()."""
    server = ThreadingHTTPServer((host, port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def server_url(server):
    return "http://127.0.0.1:%d" % server.server_address[1]


def stop_server(server):
    server.shutdown()
    server.server_close()


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        port = int(argv[0]) if argv else 8765
    except ValueError:
        print("Usage: python3 tools/mock_jev.py [port]")
        return 2
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("%s. Listening on http://127.0.0.1:%d (press Ctrl+C to stop)" % (BANNER, port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
