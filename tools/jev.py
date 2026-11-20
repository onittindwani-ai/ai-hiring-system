"""Small Jev client with no dependencies (Python 3.9+, standard library only).

Usage:
    import jev
    client = jev.JevClient()            # key from TYPESAFE_API_KEY or a local .env file
    answers, meta = client.ask("some text", {"q1": jev.noul("The text mentions a refund")})

What it does:
    Calls the Jev API (TypeSafe AI): POST {base}/v1/systemone with the key as a Bearer token. Question helpers build the three question types:
        choice(instructions, criteria)   pick one option; criteria is {option: description}
        score(instructions, levels)      rate on ordered levels; levels is a list of descriptions
        noul(instructions)               is this statement true of the text? (0 to 1)
    It retries on HTTP 429 and 529 with a growing wait. It never prints or logs a key.
    Set JEV_BASE_URL to point it at the fake practice server (tools/mock_jev.py).

Adapted from the author's earlier Jev starter kit (same author, MIT). This kit is independent
and is not made or endorsed by TypeSafe AI.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import hlib  # noqa: E402

DEFAULT_BASE_URL = "https://api.typesafe.ai"
DEFAULT_MODEL = "jev-latest"
# Price on typesafe.ai, checked on 2026-11-20: $42 per billion input tokens, output price not stated.
# Re check before you rely on it. This is a starting assumption.
PRICE_PER_MILLION_INPUT_TOKENS = 0.042
RETRY_CODES = (429, 529)


class JevError(Exception):
    """Raised for any problem calling Jev, with a message a person can act on."""


def choice(instructions, criteria):
    return {"type": "choice", "instructions": instructions, "criteria": dict(criteria)}


def score(instructions, levels):
    return {"type": "score", "instructions": instructions, "criteria": list(levels)}


def noul(instructions):
    return {"type": "noul", "instructions": instructions}


def explain_http_error(code, detail):
    """Plain words for an HTTP error. `detail` is the server text (shortened by the caller)."""
    hints = {
        400: "The request broke a rule (or the text is longer than the model accepts). ",
        401: "The API key is missing, wrong or deleted. Create a new key at console.typesafe.ai/keys. ",
        402: "The account may need credit. Add a few dollars at console.typesafe.ai/keys and try again. ",
        413: "The request body is too large. Send less text. ",
        415: "Unsupported Content-Encoding. ",
        422: "Validation failed (a required field is missing or malformed). ",
        429: "Rate limit reached. Wait and retry, or send fewer requests at once. ",
        529: "TypeSafe is temporarily overloaded. Retry in a moment. ",
    }
    return "HTTP %s. %sServer said: %s" % (code, hints.get(code, ""), detail)


def top_choice(answer):
    """Return (option, probability, confidence) for a choice answer."""
    option = answer.get("choice")
    return option, answer.get("probabilities", {}).get(option, 0.0), answer.get("confidence", 0.0)


def estimate_cost(input_tokens, price_per_million=PRICE_PER_MILLION_INPUT_TOKENS):
    """Dollars for the input tokens. Output tokens are not priced here (not stated on the price page)."""
    return input_tokens / 1_000_000 * price_per_million


class JevClient:
    def __init__(self, api_key=None, model=None, base_url=None, timeout=30, max_retries=4,
                 env_file=None, sleep=time.sleep):
        """`env_file`: a specific .env path to read. When None, the current folder's .env and the repo .env are read.
        `sleep` is injectable so tests do not wait."""
        if env_file is not None:
            hlib.load_env_file(env_file)
        else:
            hlib.load_env_file(".env")
            hlib.load_env_file(str(hlib.ROOT / ".env"))
        self._api_key = api_key or os.environ.get("TYPESAFE_API_KEY", "")
        self.model = model or os.environ.get("JEV_MODEL", DEFAULT_MODEL)
        self.base_url = (base_url or os.environ.get("JEV_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._sleep = sleep
        if not self._api_key:
            raise JevError(
                "No Jev key found. Jev is optional. To use it, set TYPESAFE_API_KEY in your own terminal "
                "(never in the AI chat) or in a local .env file. Steps: docs/JEV-OPTIONAL.md")

    def __repr__(self):
        return "JevClient(model=%r, base_url=%r, key=set)" % (self.model, self.base_url)

    def ask(self, state, questions):
        """Send one text (`state`) and named questions in one request. Returns (answers, meta).

        meta has: model, input_tokens, output_tokens, seconds (whole call, retries included).
        """
        body = json.dumps({"state": state, "model": self.model, "questions": questions}).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + "/v1/systemone", data=body, method="POST",
            headers={"Authorization": "Bearer " + self._api_key, "Content-Type": "application/json",
                     "User-Agent": "ai-hiring-system/1.0"})
        started = time.time()
        last = "unknown"
        for attempt in range(self.max_retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    data = json.loads(response.read().decode("utf-8"))
                usage = data.get("usage", {})
                meta = {"model": data.get("model", self.model),
                        "input_tokens": usage.get("input_tokens", 0),
                        "output_tokens": usage.get("output_tokens", 0),
                        "seconds": time.time() - started}
                return data.get("answers", {}), meta
            except urllib.error.HTTPError as err:
                detail = err.read().decode("utf-8", "replace")[:300]
                err.close()
                if err.code in RETRY_CODES and attempt < self.max_retries:
                    self._sleep(2 ** attempt)  # 1, 2, 4, 8 seconds
                    last = "HTTP %s" % err.code
                    continue
                raise JevError(explain_http_error(err.code, detail))
            except urllib.error.URLError as err:
                if attempt < self.max_retries:
                    self._sleep(2 ** attempt)
                    last = str(err.reason)
                    continue
                raise JevError("Could not reach %s: %s" % (self.base_url, err.reason))
            except (ValueError, json.JSONDecodeError):
                raise JevError("Jev sent back something that is not JSON. Try again, or check JEV_BASE_URL.")
        raise JevError("Gave up after %d tries (last problem: %s)." % (self.max_retries + 1, last))
