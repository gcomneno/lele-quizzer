from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from lele_quizzer.config import KnowledgeBaseConfig


@dataclass(frozen=True)
class LessonRecord:
    id: str
    text: str
    topic: str | None
    title: str | None
    tags: tuple[str, ...]
    raw: dict[str, Any]


@dataclass(frozen=True)
class KnowledgeBaseSummary:
    path: Path
    lesson_count: int
    topics: Counter[str]
    tags: Counter[str]
    lessons: tuple[LessonRecord, ...]


def load_lessons(config: KnowledgeBaseConfig) -> list[LessonRecord]:
    if config.type != "lele_manager_jsonl":
        raise ValueError(f"Unsupported knowledge base type: {config.type}")

    if not config.path.exists():
        raise FileNotFoundError(f"Knowledge base file not found: {config.path}")

    lessons: list[LessonRecord] = []

    with config.path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at line {line_number}: {exc}") from exc

            lessons.append(_record_from_raw(raw, config))

    return lessons


def inspect_knowledge_base(config: KnowledgeBaseConfig) -> KnowledgeBaseSummary:
    lessons = load_lessons(config)

    topics: Counter[str] = Counter()
    tags: Counter[str] = Counter()

    for lesson in lessons:
        topics[lesson.topic or "<missing>"] += 1
        tags.update(lesson.tags)

    return KnowledgeBaseSummary(
        path=config.path,
        lesson_count=len(lessons),
        topics=topics,
        tags=tags,
        lessons=tuple(lessons),
    )


def _record_from_raw(raw: dict[str, Any], config: KnowledgeBaseConfig) -> LessonRecord:
    raw_tags = raw.get(config.tags_column) or []
    if isinstance(raw_tags, str):
        tags = tuple(part.strip() for part in raw_tags.split(",") if part.strip())
    else:
        tags = tuple(str(tag) for tag in raw_tags if str(tag).strip())

    return LessonRecord(
        id=str(raw.get(config.id_column, "")),
        text=str(raw.get(config.text_column, "")),
        topic=_optional_str(raw.get(config.topic_column)),
        title=_optional_str(raw.get(config.title_column)),
        tags=tags,
        raw=raw,
    )


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
