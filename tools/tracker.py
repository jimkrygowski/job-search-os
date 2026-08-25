#!/usr/bin/env python3
"""CLI for reading and writing tracker.md / tracker_closed.md.

This is the only code that should ever write these files. Skills call it
via `python3 tools/tracker.py <command> ...` rather than editing the
markdown tables directly, to avoid corrupting pipeline state.
"""
import argparse
import datetime
import sys
from pathlib import Path

COLUMNS = ["Company", "Role", "Stage", "Last Activity", "Next Action", "Next Action Date"]

ACTIVE_PATH = Path("tracker.md")
CLOSED_PATH = Path("tracker_closed.md")
ACTIVE_TITLE = "Active Opportunities"
CLOSED_TITLE = "Closed Opportunities"


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def unescape_cell(value: str) -> str:
    return value.replace("\\|", "|").strip()


def split_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    parts = []
    current = ""
    i = 0
    while i < len(stripped):
        ch = stripped[i]
        if ch == "\\" and i + 1 < len(stripped) and stripped[i + 1] == "|":
            current += "\\|"
            i += 2
            continue
        if ch == "|":
            parts.append(current.strip())
            current = ""
            i += 1
            continue
        current += ch
        i += 1
    parts.append(current.strip())
    return parts


def parse_table(text: str) -> list[dict]:
    lines = [line for line in text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return []
    rows = []
    for line in lines[2:]:  # skip header + separator
        cells = split_row(line)
        if len(cells) != len(COLUMNS):
            raise ValueError(
                f"Malformed row (expected {len(COLUMNS)} columns, got {len(cells)}): {line!r}"
            )
        rows.append({col: unescape_cell(cell) for col, cell in zip(COLUMNS, cells)})
    return rows


def serialize_table(rows: list[dict], title: str) -> str:
    header = "| " + " | ".join(COLUMNS) + " |"
    separator = "| " + " | ".join(["---"] * len(COLUMNS)) + " |"
    lines = [f"# {title}", "", header, separator]
    for row in rows:
        cells = [escape_cell(row.get(col, "")) for col in COLUMNS]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def read_table(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return parse_table(path.read_text())


def write_table(path: Path, rows: list[dict], title: str) -> None:
    path.write_text(serialize_table(rows, title))


def find_row(rows, company, role):
    for row in rows:
        if row["Company"] == company and row["Role"] == role:
            return row
    return None


def today() -> str:
    return datetime.date.today().isoformat()


def cmd_add(args):
    rows = read_table(ACTIVE_PATH)
    if find_row(rows, args.company, args.role):
        print(
            f"error: {args.company} / {args.role} already exists in tracker.md "
            "— use update-status",
            file=sys.stderr,
        )
        sys.exit(1)
    rows.append({
        "Company": args.company,
        "Role": args.role,
        "Stage": args.stage,
        "Last Activity": args.last_activity or today(),
        "Next Action": args.next_action or "",
        "Next Action Date": args.next_action_date or "",
    })
    write_table(ACTIVE_PATH, rows, ACTIVE_TITLE)
    print(f"added {args.company} / {args.role}")


def cmd_update_status(args):
    rows = read_table(ACTIVE_PATH)
    row = find_row(rows, args.company, args.role)
    if row is None:
        print(f"error: {args.company} / {args.role} not found in tracker.md", file=sys.stderr)
        sys.exit(1)
    row["Stage"] = args.stage
    if args.next_action is not None:
        row["Next Action"] = args.next_action
    if args.next_action_date is not None:
        row["Next Action Date"] = args.next_action_date
    row["Last Activity"] = args.last_activity or today()
    write_table(ACTIVE_PATH, rows, ACTIVE_TITLE)
    print(f"updated {args.company} / {args.role} -> {args.stage}")


def cmd_record_event(args):
    rows = read_table(ACTIVE_PATH)
    row = find_row(rows, args.company, args.role)
    if row is None:
        print(f"error: {args.company} / {args.role} not found in tracker.md", file=sys.stderr)
        sys.exit(1)
    row["Next Action"] = args.event
    row["Next Action Date"] = args.date
    row["Last Activity"] = today()
    write_table(ACTIVE_PATH, rows, ACTIVE_TITLE)
    print(f"recorded event for {args.company} / {args.role}: {args.event} ({args.date})")


def cmd_close(args):
    rows = read_table(ACTIVE_PATH)
    row = find_row(rows, args.company, args.role)
    if row is None:
        print(f"error: {args.company} / {args.role} not found in tracker.md", file=sys.stderr)
        sys.exit(1)
    rows.remove(row)
    write_table(ACTIVE_PATH, rows, ACTIVE_TITLE)

    closed_rows = read_table(CLOSED_PATH)
    closed_rows.append(row)
    write_table(CLOSED_PATH, closed_rows, CLOSED_TITLE)

    notes_dir = Path("opportunity") / args.company / args.role
    notes_dir.mkdir(parents=True, exist_ok=True)
    notes_path = notes_dir / "notes.md"
    with notes_path.open("a") as f:
        f.write(f"\n- **Closed ({today()}):** {args.reason}\n")

    print(f"closed {args.company} / {args.role}: {args.reason}")


def cmd_list(args):
    path = CLOSED_PATH if args.closed else ACTIVE_PATH
    title = CLOSED_TITLE if args.closed else ACTIVE_TITLE
    rows = read_table(path)
    print(serialize_table(rows, title))


def build_parser():
    parser = argparse.ArgumentParser(description="Manage tracker.md / tracker_closed.md")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add")
    p_add.add_argument("company")
    p_add.add_argument("role")
    p_add.add_argument("--stage", required=True)
    p_add.add_argument("--next-action", default="")
    p_add.add_argument("--next-action-date", default="")
    p_add.add_argument("--last-activity")
    p_add.set_defaults(func=cmd_add)

    p_update = sub.add_parser("update-status")
    p_update.add_argument("company")
    p_update.add_argument("role")
    p_update.add_argument("--stage", required=True)
    p_update.add_argument("--next-action")
    p_update.add_argument("--next-action-date")
    p_update.add_argument("--last-activity")
    p_update.set_defaults(func=cmd_update_status)

    p_event = sub.add_parser("record-event")
    p_event.add_argument("company")
    p_event.add_argument("role")
    p_event.add_argument("--event", required=True)
    p_event.add_argument("--date", required=True)
    p_event.set_defaults(func=cmd_record_event)

    p_close = sub.add_parser("close")
    p_close.add_argument("company")
    p_close.add_argument("role")
    p_close.add_argument("--reason", required=True)
    p_close.set_defaults(func=cmd_close)

    p_list = sub.add_parser("list")
    p_list.add_argument("--closed", action="store_true")
    p_list.set_defaults(func=cmd_list)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
