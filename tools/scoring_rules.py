"""Offline scoring baseline: keywords plus sentence level evidence (Python 3.9+, standard library only).

Usage:
    from scoring_rules import score_criteria, find_evidence, resolve_gate, resolve_deal_breaker
    (used by tools/score_candidates.py with --engine rules; no network, no key)

What it does:
    Gives each criterion a level from 0 to 4 and a confidence from 0 to 1, the same way every time:
      * It splits the text into sentences and looks for the scorecard keywords.
      * A keyword inside a skills list (a line with many commas or a "Skills:" label) counts as
        "mentioned only", so stuffing keywords does not raise the level above 1.
      * The level comes from how many DIFFERENT keywords appear in real sentences, and from signs of
        ownership (verbs like led, built, ran, wrote, fixed) and impact (a number, taught, improved).
      * Very short text lowers the confidence, so a thin resume goes to a person.
    It is a rough, honest baseline. It cannot read between the lines, understand synonyms the scorecard
    does not list, or judge quality. A person decides.
"""
import re

OWNERSHIP_RE = re.compile(
    r"\b(?:led|lead|leading|built|ran|owned|launch\w*|creat\w*|design\w*|manag\w*|closed|wrote|set up|grew|drove|"
    r"improv\w*|reduc\w*|increas\w*|train\w*|taught|negotiat\w*|reconcil\w*|deliver\w*|implement\w*|develop\w*|"
    r"shipped|handl\w*|book\w*|generat\w*|produc\w*|resolv\w*|fixed|diagnos\w*|debug\w*|investigat\w*|automat\w*|"
    r"organi[sz]\w*|prepar\w*|process\w*|maintain\w*|coordinat\w*|cut|saved|won|hired|mentor\w*|coach\w*|presented|"
    r"research\w*|analy[sz]\w*|configur\w*|deploy\w*|migrat\w*|draft\w*|publish\w*|answer\w*|review\w*|audit\w*|"
    r"streamlin\w*|introduc\w*|establish\w*|rebuilt|replaced|opened|sold|called|emailed|visited|cleaned|repaired)\b",
    re.IGNORECASE)
IMPACT_RE = re.compile(
    r"(?<![\d.])(?!(?:19|20)\d\d\b)\d+(?:[.,]\d+)?\s?%?|\b(?:taught|mentor\w*|coach\w*|trained others|improv\w*|"
    r"reduc\w*|increas\w*|saved|doubled|halved|documented|playbook|checklist|first)\b", re.IGNORECASE)
LIST_LABEL_RE = re.compile(r"^\s*(?:core\s+)?(?:skills?|tools?|keywords?|technologies|tech stack|competencies|expertise)\b\s*[:|]",
                           re.IGNORECASE)
NEGATION_RE = re.compile(r"\b(?:no|not|cannot|can't|cant|unable|never|without|don't|dont|won't|wont)\b", re.IGNORECASE)
POSITIVE_RE = re.compile(r"\b(?:yes|y|true|authori[sz]ed|eligible|citizen|resident|available|willing|able|can|have|hold|holds)\b",
                         re.IGNORECASE)
STOP = set("the and for with that this from have has are was were can the person role your their into who what when".split())
THIN_WORDS = 80


def sentences(text):
    """Split into sentences or list lines, bullets removed. Order is kept."""
    out = []
    for line in str(text or "").splitlines():
        line = re.sub(r"^\s*(?:[-*" + chr(0x2022) + r"]|\d+[.)])\s+", "", line).strip()
        if not line:
            continue
        if LIST_LABEL_RE.match(line) or line.count(",") >= 5 or line.count("|") >= 3:
            out.append(line)
            continue
        out.extend(p.strip() for p in re.split(r"(?<=[.!?])\s+", line) if p.strip())
    return out


def is_list_like(sentence):
    return bool(LIST_LABEL_RE.match(sentence)) or sentence.count(",") >= 4 or sentence.count("|") >= 3 \
        or sentence.count(";") >= 3


def _has_keyword(sentence_lower, keyword):
    return re.search(r"(?<![a-z0-9])" + re.escape(keyword.lower()), sentence_lower) is not None


def find_evidence(text, keywords, limit=160):
    """The best sentence showing the keywords, as a short quote. Empty string if none.
    Prefers real sentences (not skills lists) with the most different keywords."""
    best, best_key = "", (-1, -1)
    for sentence in sentences(text):
        lower = sentence.lower()
        hits = sum(1 for k in keywords if _has_keyword(lower, k))
        if not hits:
            continue
        key = (0 if is_list_like(sentence) else 1, hits)
        if key > best_key:
            best, best_key = sentence, key
    best = re.sub(r"\s+", " ", best).strip()
    return best if len(best) <= limit else best[:limit - 3].rstrip() + "..."


def level_for(used, own, impact, listed):
    """Level 0 to 4 from: distinct keywords in real sentences, ownership, impact, and keywords only in lists."""
    if used == 0:
        return 1 if listed else 0
    if not own:
        return 1 if used == 1 else 2
    base = 2 if used == 1 else 3
    return min(4, base + (1 if impact and used >= 2 else 0))


def count_distinct(used):
    """Number of different keywords, counting a phrase and its plural or longer form once (cold call, cold calls)."""
    kept = []
    for word in sorted(used, key=len):
        if not any(word.startswith(other) for other in kept):
            kept.append(word)
    return len(kept)


def score_criterion(criterion, sents, word_count):
    keywords = criterion.get("keywords", [])
    used, listed, evidence_sents = set(), set(), []
    own = impact = False
    for sentence in sents:
        lower = sentence.lower()
        hits = [k for k in keywords if _has_keyword(lower, k)]
        if not hits:
            continue
        if is_list_like(sentence):
            listed.update(hits)
            continue
        used.update(hits)
        evidence_sents.append(sentence)
        own = own or bool(OWNERSHIP_RE.search(sentence))
        impact = impact or bool(IMPACT_RE.search(sentence))
    distinct = count_distinct(used)
    level = level_for(distinct, own, impact, bool(listed - used))
    if level == 0 or (distinct == 0 and listed):
        confidence = 0.65 if listed else 0.6  # a skills list alone is a fairly clear "mentioned only"
    else:
        confidence = min(0.9, 0.5 + 0.1 * min(distinct, 3) + (0.1 if own else 0.0))
    if word_count < THIN_WORDS:
        confidence = min(confidence, 0.5)
    quote = find_evidence("\n".join(sents), keywords) if level > 0 else ""
    return {"level": level, "confidence": round(confidence, 2), "evidence": quote}


def score_criteria(scorecard, text):
    """Dict of criterion id to {"level", "confidence", "evidence"} for every criterion."""
    sents = sentences(text)
    words = len(re.findall(r"\w+", str(text or "")))
    return {c["id"]: score_criterion(c, sents, words) for c in scorecard["criteria"]}


def normalise_answer(value):
    """Turn yes, no, true, false and similar into 'yes', 'no' or 'unknown'."""
    if isinstance(value, bool):
        return "yes" if value else "no"
    word = str(value or "").strip().lower().rstrip(".!")
    if word in ("yes", "y", "true", "1"):
        return "yes"
    if word in ("no", "n", "false", "0"):
        return "no"
    return "unknown"


def _stems(text):
    return {w[:5] for w in re.findall(r"[a-z]{3,}", str(text).lower()) if w not in STOP}


def _explicit(candidate, key):
    answers = candidate.get("answers") or {}
    for name, value in answers.items():
        if str(name).strip().lower() == key.lower():
            return normalise_answer(value)
    return "unknown"


def resolve_gate(gate, candidate, text):
    """'yes', 'no' or 'unknown' for a gate. Uses an answer named like the gate id, else a plain sentence
    that mentions the gate words with a clear yes or no cue. Never guesses from silence."""
    explicit = _explicit(candidate, gate["id"])
    if explicit != "unknown":
        return explicit
    wanted = _stems(gate["id"].replace("_", " "))
    if not wanted:
        return "unknown"
    for sentence in sentences(text):
        if wanted <= _stems(sentence):
            if NEGATION_RE.search(sentence):
                return "no"
            if POSITIVE_RE.search(sentence):
                return "yes"
    return "unknown"


def resolve_deal_breaker(item, candidate, text):
    """'yes' only when the candidate says so (an answer named like the id, or a sentence that holds most of the
    words of the description with no negation). Otherwise 'no': nothing shown, nothing assumed."""
    explicit = _explicit(candidate, item["id"])
    if explicit != "unknown":
        return explicit
    wanted = _stems(item.get("description", ""))
    if len(wanted) < 2:
        return "no"
    for sentence in sentences(text):
        have = len(wanted & _stems(sentence))
        if have >= 2 and have / len(wanted) >= 0.7 and not NEGATION_RE.search(sentence):
            return "yes"
    return "no"
