from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from lele_quizzer.config import load_config
from lele_quizzer.kb import inspect_knowledge_base


DEFAULT_CONFIG = Path("lele-quizzer.yaml")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "kb" and args.kb_command == "inspect":
        return _kb_inspect(args)

    parser.error("unknown command")
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lele-quizzer",
        description="Quiz layer for LeLe Manager knowledge bases.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"Config YAML path. Default: {DEFAULT_CONFIG}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    kb_parser = subparsers.add_parser("kb", help="Knowledge-base commands.")
    kb_subparsers = kb_parser.add_subparsers(dest="kb_command", required=True)
    kb_subparsers.add_parser("inspect", help="Inspect configured knowledge base.")

    return parser


def _kb_inspect(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    summary = inspect_knowledge_base(config.knowledge_base)

    print("=== LeLe Quizzer knowledge base ===")
    print(f"path: {summary.path}")
    print(f"type: {config.knowledge_base.type}")
    print(f"lessons: {summary.lesson_count}")
    print()

    print("=== topics ===")
    for topic, count in summary.topics.most_common():
        print(f"{count:3}  {topic}")
    print()

    print("=== tags ===")
    if summary.tags:
        for tag, count in summary.tags.most_common(20):
            print(f"{count:3}  {tag}")
    else:
        print("<no tags>")
    print()

    print("=== first lessons ===")
    for lesson in summary.lessons[:10]:
        title = lesson.title or "-"
        topic = lesson.topic or "-"
        print(f"- {lesson.id} | topic={topic} | title={title}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
