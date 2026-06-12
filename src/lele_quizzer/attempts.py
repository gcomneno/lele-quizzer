from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json


@dataclass(frozen=True)
class QuizAttempt:
    created_at: str
    query: str
    lesson_id: str
    topic: str
    title: str
    prompt: str
    answer: str


def new_attempt(
    *,
    query: str,
    lesson_id: str,
    topic: str,
    title: str,
    prompt: str,
    answer: str,
) -> QuizAttempt:
    return QuizAttempt(
        created_at=datetime.now(timezone.utc).isoformat(),
        query=query,
        lesson_id=lesson_id,
        topic=topic,
        title=title,
        prompt=prompt,
        answer=answer,
    )


def append_attempt(path: Path, attempt: QuizAttempt) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(asdict(attempt), ensure_ascii=False) + "\n")
