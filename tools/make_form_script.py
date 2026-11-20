"""Form script maker: turn a form description into a Google Apps Script you paste yourself.

Usage:
    python3 tools/make_form_script.py templates/forms/application-form.json
    python3 tools/make_form_script.py <form.json> --out hiring/<role>/create-form.gs
    python3 tools/make_form_script.py <form.json> --vars company.json --out hiring/<role>/create-form.gs

What it does:
    Reads a form description (title, description, sections, questions) and writes a Google Apps
    Script. You paste it into script.google.com in your own Google account and press Run. It then
    creates the Google Form and a linked Google Sheet for the responses. No browser extension is
    needed and nothing is sent anywhere by this tool. Question types: short_text, paragraph,
    multiple_choice, checkbox, file_upload, email, url. Apps Script cannot create file upload
    questions, so a file_upload question becomes a link question and the script says so in a comment.
    The tool also warns (it does not block) about questions that look like protected traits.
    Form shape: {"title", "description", "sections": [{"title", "description", "questions": [...]}]}
    or a flat {"questions": [...]}. A question has "text" (or "label" or "question"), "type", "required",
    and "options" for choice types. {{placeholders}} in the text can be filled with --vars (a JSON file);
    leftovers are listed as a warning so you do not publish them by accident.
"""
import argparse
import json
import re
import sys
from pathlib import Path

QUESTION_TYPES = ["short_text", "paragraph", "multiple_choice", "checkbox", "file_upload", "email", "url"]
PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")
RISKY_WORDS = ["date of birth", "birth date", "age", "gender", "sex", "marital", "religion", "race", "ethnic",
               "nationality", "photo", "pregnan", "disability", "health", "children", "family status", "maiden"]


def js(value):
    """A safe JavaScript string literal."""
    return json.dumps(str(value), ensure_ascii=True)


def question_text(question):
    return str(question.get("text") or question.get("question") or question.get("title") or question.get("label") or "").strip()


def normalize_sections(form):
    if form.get("sections"):
        return [{"title": s.get("title", ""), "description": s.get("description", ""),
                 "questions": list(s.get("questions", []))} for s in form["sections"]]
    return [{"title": "", "description": "", "questions": list(form.get("questions", []))}]


def validate(form):
    """Return a list of user fixable problems."""
    problems = []
    if not isinstance(form, dict) or not form.get("title"):
        problems.append("The form needs a title.")
        return problems
    sections = normalize_sections(form)
    total = 0
    for s_index, section in enumerate(sections, start=1):
        for q_index, question in enumerate(section["questions"], start=1):
            total += 1
            label = "section %d question %d" % (s_index, q_index)
            if not question_text(question):
                problems.append("%s has no text." % label)
            kind = question.get("type", "short_text")
            if kind not in QUESTION_TYPES:
                problems.append("%s has unknown type '%s' (use one of: %s)." % (label, kind, ", ".join(QUESTION_TYPES)))
            if kind in ("multiple_choice", "checkbox") and len(question.get("options") or question.get("choices") or []) < 2:
                problems.append("%s needs at least 2 options." % label)
    if total == 0:
        problems.append("The form has no questions.")
    return problems


def risky_warnings(form):
    warnings = []
    for section in normalize_sections(form):
        for question in section["questions"]:
            text = " " + question_text(question).lower() + " "
            for word in RISKY_WORDS:
                if (" %s " % word) in text or (" %ss " % word) in text or (len(word) > 5 and word in text):
                    warnings.append("Question '%s' may ask about a protected trait ('%s'). Ask only job related things."
                                    % (question_text(question), word))
                    break
    return warnings


def fill_vars(node, values):
    """Return a copy of the form with {{name}} replaced where a value is given."""
    if isinstance(node, str):
        return PLACEHOLDER_RE.sub(lambda m: str(values[m.group(1)]) if str(values.get(m.group(1), "")).strip() else m.group(0), node)
    if isinstance(node, list):
        return [fill_vars(item, values) for item in node]
    if isinstance(node, dict):
        return {key: fill_vars(value, values) for key, value in node.items()}
    return node


def unfilled_placeholders(form):
    found = []
    for name in PLACEHOLDER_RE.findall(json.dumps(form)):
        if name not in found:
            found.append(name)
    return found


def emit_question(question, index):
    text = question_text(question)
    kind = question.get("type", "short_text")
    required = "true" if question.get("required") else "false"
    help_text = question.get("help") or question.get("description") or ""
    options = question.get("options") or question.get("choices") or []
    lines = []
    if kind == "file_upload":
        lines += ["  // Apps Script cannot create file upload questions. Using a link question instead.",
                  "  // Tell people to share the file (for example from their own Drive or a portfolio site) and paste the link."]
        item_call, extra = "addTextItem", ["item.setValidation(FormApp.createTextValidation().requireTextIsUrl().build());"]
        text = text + " (paste a link to the file)"
    elif kind == "paragraph":
        item_call, extra = "addParagraphTextItem", []
    elif kind == "multiple_choice":
        item_call, extra = "addMultipleChoiceItem", ["item.setChoiceValues(%s);" % json.dumps([str(o) for o in options], ensure_ascii=True)]
    elif kind == "checkbox":
        item_call, extra = "addCheckboxItem", ["item.setChoiceValues(%s);" % json.dumps([str(o) for o in options], ensure_ascii=True)]
    elif kind == "email":
        item_call, extra = "addTextItem", ["item.setValidation(FormApp.createTextValidation().requireTextIsEmail().build());"]
    elif kind == "url":
        item_call, extra = "addTextItem", ["item.setValidation(FormApp.createTextValidation().requireTextIsUrl().build());"]
    else:
        item_call, extra = "addTextItem", []
    lines.append("  item = form.%s();" % item_call)
    lines.append("  item.setTitle(%s).setRequired(%s);" % (js(text), required))
    if help_text:
        lines.append("  item.setHelpText(%s);" % js(help_text))
    lines += ["  " + e for e in extra]
    return lines


def generate(form):
    title = form["title"]
    lines = [
        "// Generated by tools/make_form_script.py. Read it, then run it in your own Google account.",
        "// How to use: open script.google.com, create a new project, paste this file, press Run on createApplicationForm,",
        "// approve the Google permission prompt, then open the Logs to find the edit and share links.",
        "// It creates one Google Form and one Google Sheet for responses. It sends nothing to anyone.",
        "",
        "function createApplicationForm() {",
        "  var form = FormApp.create(%s);" % js(title),
        "  form.setDescription(%s);" % js(form.get("description", "")),
        "  form.setCollectEmail(false);",
        "  var item;",
    ]
    for s_index, section in enumerate(normalize_sections(form)):
        if section["title"]:
            if s_index == 0:
                lines.append("  item = form.addSectionHeaderItem();")
            else:
                lines.append("  item = form.addPageBreakItem();")
            lines.append("  item.setTitle(%s);" % js(section["title"]))
            if section["description"]:
                lines.append("  item.setHelpText(%s);" % js(section["description"]))
        for q_index, question in enumerate(section["questions"]):
            lines += emit_question(question, q_index)
    if form.get("confirmation_message"):
        lines.append("  form.setConfirmationMessage(%s);" % js(form["confirmation_message"]))
    lines += [
        "  var sheet = SpreadsheetApp.create(%s);" % js(title + " (responses)"),
        "  form.setDestination(FormApp.DestinationType.SPREADSHEET, sheet.getId());",
        "  Logger.log('Edit the form here: ' + form.getEditUrl());",
        "  Logger.log('Share this link with applicants: ' + form.getPublishedUrl());",
        "  Logger.log('Responses sheet: ' + sheet.getUrl());",
        "}",
        "",
    ]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Make a Google Apps Script that creates the application form")
    parser.add_argument("form")
    parser.add_argument("--out")
    parser.add_argument("--vars", help="JSON file that fills {{placeholders}} in the form text")
    args = parser.parse_args(argv)
    path = Path(args.form)
    if not path.exists():
        print("Form file not found: %s" % path)
        return 1
    try:
        form = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print("That file is not valid JSON: %s" % exc)
        return 1
    if args.vars:
        try:
            form = fill_vars(form, json.loads(Path(args.vars).read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError, AttributeError) as exc:
            print("Could not read the variables file: %s" % exc)
            return 1
    problems = validate(form)
    if problems:
        print("Fix these first:")
        for problem in problems:
            print("  - " + problem)
        return 1
    left = unfilled_placeholders(form)
    if left:
        print("WARNING: these {{placeholders}} are still in the form text, fill them with --vars: %s" % ", ".join(left),
              file=sys.stderr)
    for warning in risky_warnings(form):
        print("WARNING: " + warning, file=sys.stderr)
    script = generate(form)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(script, encoding="utf-8")
        print("Wrote %s. Paste it into script.google.com and press Run." % args.out)
    else:
        print(script)
    return 0


if __name__ == "__main__":
    sys.exit(main())
