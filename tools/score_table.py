#!/usr/bin/env python3
"""Parse state/career/trajectory.md into scoring criteria and render a
fixed-format Markdown score table.

score-opportunity shells out to this rather than freehand-formatting a
table itself, so the criteria list always matches trajectory.md verbatim
and the table layout never drifts between scoring sessions.
"""
import argparse
import json
import re
import sys
from pathlib import Path

TRAJECTORY_PATH = Path("state/career/trajectory.md")

SCORES = ["Meets", "Partial", "Fails", "Unknown"]
SCORE_EMOJI = {"Meets": "✅", "Partial": "⚠️", "Fails": "❌", "Unknown": "❓"}

# (heading in trajectory.md, category label, "bullets" or "paragraph")
CRITERIA_SECTIONS = [
    ("Must-Haves", "Must-Have", "bullets"),
    ("Must-Nots", "Must-Not", "bullets"),
    ("Short-Term Goal (Next Role)", "Short-Term Goal", "paragraph"),
]


def _section_body(trajectory_text, heading):
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(trajectory_text)
    return m.group(1).strip("\n") if m else None


def _parse_bullets(body):
    bullets = []
    for line in body.splitlines():
        if line.startswith("- "):
            bullets.append(line[2:].strip())
        elif line.strip() and bullets:
            bullets[-1] += " " + line.strip()
    return bullets


def _parse_paragraph(body):
    para = body.split("\n\n", 1)[0]
    return " ".join(para.split())


def parse_criteria(trajectory_text):
    criteria = []
    for heading, category, kind in CRITERIA_SECTIONS:
        body = _section_body(trajectory_text, heading)
        if body is None:
            continue
        slug = category.lower().replace(" ", "-")
        if kind == "bullets":
            for i, text in enumerate(_parse_bullets(body), start=1):
                criteria.append({"id": f"{slug}-{i}", "category": category, "text": text})
        else:
            text = _parse_paragraph(body)
            if text:
                criteria.append({"id": slug, "category": category, "text": text})
    return criteria


def _escape_cell(text):
    return " ".join(text.split()).replace("|", "\\|")


def render_table(criteria, scores):
    criteria_by_id = {c["id"]: c for c in criteria}

    scores_by_id = {}
    for s in scores:
        cid = s.get("id")
        if cid not in criteria_by_id:
            raise ValueError(f"unknown criterion id: {cid!r}")
        raw_score = s.get("score", "")
        normalized = raw_score.strip().title() if isinstance(raw_score, str) else raw_score
        if normalized not in SCORES:
            raise ValueError(
                f"invalid score {raw_score!r} for {cid!r}: must be one of {SCORES}"
            )
        scores_by_id[cid] = {"score": normalized, "rationale": s.get("rationale", "")}

    missing = [c["id"] for c in criteria if c["id"] not in scores_by_id]
    if missing:
        raise ValueError(f"missing scores for criteria: {missing}")

    lines = ["| Criterion | Score | Rationale |", "| --- | --- | --- |"]
    for c in criteria:
        s = scores_by_id[c["id"]]
        criterion_cell = _escape_cell(f"**{c['category']}:** {c['text']}")
        score_cell = f"{SCORE_EMOJI[s['score']]} {s['score']}"
        rationale_cell = _escape_cell(s["rationale"])
        lines.append(f"| {criterion_cell} | {score_cell} | {rationale_cell} |")
    return "\n".join(lines)


def _read_trajectory():
    if not TRAJECTORY_PATH.exists():
        print(f"{TRAJECTORY_PATH} not found", file=sys.stderr)
        sys.exit(1)
    return TRAJECTORY_PATH.read_text()


def cmd_criteria(args):
    criteria = parse_criteria(_read_trajectory())
    print(json.dumps(criteria, indent=2))


def cmd_render(args):
    criteria = parse_criteria(_read_trajectory())
    try:
        scores = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"invalid JSON on stdin: {e}", file=sys.stderr)
        sys.exit(1)
    try:
        table = render_table(criteria, scores)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    print(table)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Parse trajectory.md into scoring criteria and render a fixed-format score table"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_criteria = sub.add_parser("criteria", help="print criteria parsed from trajectory.md as JSON")
    p_criteria.set_defaults(func=cmd_criteria)

    p_render = sub.add_parser("render", help="read {id, score, rationale} JSON on stdin, print the score table")
    p_render.set_defaults(func=cmd_render)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
