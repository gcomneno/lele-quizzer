from __future__ import annotations

from collections import Counter
import argparse
from pathlib import Path
from typing import Sequence

from lele_quizzer.attempts import (
    append_attempt,
    load_attempts,
    new_attempt,
    summarize_attempts,
)
from lele_quizzer.config import load_config
from lele_quizzer.kb import inspect_knowledge_base, search_lessons
from lele_quizzer.quiz import draft_questions


DEFAULT_CONFIG = Path("lele-quizzer.yaml")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "kb" and args.kb_command == "inspect":
        return _kb_inspect(args)
    if args.command == "kb" and args.kb_command == "search":
        return _kb_search(args)
    if args.command == "quiz" and args.quiz_command == "draft":
        return _quiz_draft(args)
    if args.command == "quiz" and args.quiz_command == "play":
        return _quiz_play(args)
    if args.command == "quiz" and args.quiz_command == "attempts":
        return _quiz_attempts(args)
    if args.command == "quiz" and args.quiz_command == "weaknesses":
        return _quiz_weaknesses(args)

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

    search_parser = kb_subparsers.add_parser(
        "search",
        help="Search lessons in the configured knowledge base.",
    )
    search_parser.add_argument("query", help="Text query to search for.")
    search_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of results. Default: 10.",
    )

    quiz_parser = subparsers.add_parser("quiz", help="Quiz commands.")
    quiz_subparsers = quiz_parser.add_subparsers(dest="quiz_command", required=True)

    draft_parser = quiz_subparsers.add_parser(
        "draft",
        help="Draft quiz questions from a search query.",
    )
    draft_parser.add_argument(
        "query", help="Topic or text query to draft questions from."
    )
    draft_parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of draft questions. Default: 5.",
    )

    play_parser = quiz_subparsers.add_parser(
        "play",
        help="Play an interactive terminal quiz from a search query.",
    )
    play_parser.add_argument("query", help="Topic or text query to play from.")
    play_parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Maximum number of questions. Default: 3.",
    )

    attempts_parser = quiz_subparsers.add_parser(
        "attempts",
        help="Show saved quiz attempts.",
    )
    attempts_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of attempts to show. Default: 10.",
    )

    weaknesses_parser = quiz_subparsers.add_parser(
        "weaknesses",
        help="Summarize saved quiz attempts.",
    )
    weaknesses_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of recent attempts to summarize. Default: 50.",
    )
    weaknesses_parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Maximum number of rows per section. Default: 10.",
    )

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


def _kb_search(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    results = search_lessons(
        config.knowledge_base,
        args.query,
        limit=args.limit,
    )

    print("=== LeLe Quizzer search ===")
    print(f"query: {args.query}")
    print(f"results: {len(results)}")
    print()

    if not results:
        print("<no results>")
        return 0

    for result in results:
        lesson = result.lesson
        title = lesson.title or "-"
        topic = lesson.topic or "-"
        matched = ", ".join(result.matched_terms)
        preview = lesson.text.replace("\n", " ")
        if len(preview) > 160:
            preview = preview[:157] + "..."

        print(f"- {lesson.id} | score={result.score} | topic={topic}")
        print(f"  title: {title}")
        print(f"  matched: {matched}")
        print(f"  preview: {preview}")
        print()

    return 0


def _quiz_draft(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    questions = draft_questions(
        config.knowledge_base,
        args.query,
        limit=args.limit,
    )

    print("=== LeLe Quizzer quiz draft ===")
    print(f"query: {args.query}")
    print(f"questions: {len(questions)}")
    print()

    if not questions:
        print("<no questions>")
        return 0

    for index, question in enumerate(questions, start=1):
        print(f"Domanda {index}")
        print(f"Fonte: {question.lesson_id}")
        print(f"Topic: {question.topic}")
        print(f"Titolo: {question.title}")
        print(f"Q: {question.prompt}")
        print(f"Contesto: {question.context_preview}")
        print()

    return 0


def _quiz_play(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    questions = draft_questions(
        config.knowledge_base,
        args.query,
        limit=args.limit,
    )

    attempts_path = config.quizzer.data_dir / "attempts.jsonl"

    print("=== LeLe Quizzer quiz play ===")
    print(f"query: {args.query}")
    print(f"questions: {len(questions)}")
    print(f"attempts: {attempts_path}")
    print()

    if not questions:
        print("<no questions>")
        return 0

    for index, question in enumerate(questions, start=1):
        print(f"Domanda {index}/{len(questions)}")
        print(f"Fonte: {question.lesson_id}")
        print(f"Topic: {question.topic}")
        print(f"Q: {question.prompt}")
        print()
        answer = input("Risposta: ").strip()

        attempt = new_attempt(
            query=args.query,
            lesson_id=question.lesson_id,
            topic=question.topic,
            title=question.title,
            prompt=question.prompt,
            answer=answer,
        )
        append_attempt(attempts_path, attempt)

        print("[ok] Risposta salvata.")
        print()

    print("Quiz terminato.")
    return 0


def _quiz_attempts(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    attempts_path = config.quizzer.data_dir / "attempts.jsonl"
    attempts = load_attempts(attempts_path, limit=args.limit)

    print("=== LeLe Quizzer attempts ===")
    print(f"path: {attempts_path}")
    print(f"attempts: {len(attempts)}")
    print()

    if not attempts:
        print("<no attempts>")
        return 0

    for index, attempt in enumerate(attempts, start=1):
        answer = attempt.answer.replace("\n", " ")
        if len(answer) > 160:
            answer = answer[:157] + "..."

        print(f"Tentativo {index}")
        print(f"Quando: {attempt.created_at}")
        print(f"Query: {attempt.query}")
        print(f"Fonte: {attempt.lesson_id}")
        print(f"Topic: {attempt.topic}")
        print(f"Titolo: {attempt.title}")
        print(f"Q: {attempt.prompt}")
        print(f"A: {answer}")
        print()

    return 0


def _quiz_weaknesses(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    attempts_path = config.quizzer.data_dir / "attempts.jsonl"
    summary = summarize_attempts(attempts_path, limit=args.limit)

    print("=== LeLe Quizzer weaknesses ===")
    print(f"path: {attempts_path}")
    print(f"attempts: {summary.total_attempts}")
    print(f"limit: {args.limit}")
    print()

    if summary.total_attempts == 0:
        print("<no attempts>")
        return 0

    _print_counter_section("Topics", summary.topics, args.top)
    _print_counter_section("Lessons", summary.lesson_ids, args.top)
    _print_counter_section("Queries", summary.queries, args.top)

    return 0


def _print_counter_section(title: str, counter: Counter[str], top: int) -> None:
    print(f"=== {title} ===")
    for value, count in counter.most_common(top):
        print(f"{count:3}  {value}")
    print()


if __name__ == "__main__":
    raise SystemExit(main())
