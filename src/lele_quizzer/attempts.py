from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True)
class QuizAttempt:
    created_at: str
    query: str
    lesson_id: str
    topic: str
    title: str
    question_type: str
    prompt: str
    answer: str


@dataclass(frozen=True)
class WeaknessSummary:
    total_attempts: int
    topics: Counter[str]
    lesson_ids: Counter[str]
    queries: Counter[str]


def new_attempt(
    *,
    query: str,
    lesson_id: str,
    topic: str,
    title: str,
    question_type: str,
    prompt: str,
    answer: str,
) -> QuizAttempt:
    return QuizAttempt(
        created_at=datetime.now(timezone.utc).isoformat(),
        query=query,
        lesson_id=lesson_id,
        topic=topic,
        title=title,
        question_type=question_type,
        prompt=prompt,
        answer=answer,
    )


def append_attempt(path: Path, attempt: QuizAttempt) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(asdict(attempt), ensure_ascii=False) + "\n")


def load_attempts(path: Path, *, limit: int | None = None) -> list[QuizAttempt]:
    if not path.exists():
        return []

    attempts: list[QuizAttempt] = []

    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid attempts JSONL at line {line_number}: {exc}"
                ) from exc

            attempts.append(_attempt_from_raw(raw))

    if limit is None:
        return attempts

    return attempts[-limit:]


def summarize_attempts(path: Path, *, limit: int | None = None) -> WeaknessSummary:
    attempts = load_attempts(path, limit=limit)

    return WeaknessSummary(
        total_attempts=len(attempts),
        topics=Counter(_visible_value(attempt.topic) for attempt in attempts),
        lesson_ids=Counter(_visible_value(attempt.lesson_id) for attempt in attempts),
        queries=Counter(_visible_value(attempt.query) for attempt in attempts),
    )


def _attempt_from_raw(raw: dict[str, Any]) -> QuizAttempt:
    return QuizAttempt(
        created_at=str(raw.get("created_at", "")),
        query=str(raw.get("query", "")),
        lesson_id=str(raw.get("lesson_id", "")),
        topic=str(raw.get("topic", "")),
        title=str(raw.get("title", "")),
        question_type=str(raw.get("question_type", "open_explanation")),
        prompt=str(raw.get("prompt", "")),
        answer=str(raw.get("answer", "")),
    )


def _visible_value(value: str) -> str:
    return value if value else "<missing>"
