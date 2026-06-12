from __future__ import annotations

from dataclasses import dataclass

from lele_quizzer.config import KnowledgeBaseConfig
from lele_quizzer.kb import LessonRecord, search_lessons


@dataclass(frozen=True)
class DraftQuestion:
    lesson_id: str
    title: str
    topic: str
    prompt: str
    context_preview: str


def draft_questions(
    config: KnowledgeBaseConfig,
    query: str,
    *,
    limit: int = 5,
) -> list[DraftQuestion]:
    results = search_lessons(config, query, limit=limit)

    return [_draft_question_from_lesson(result.lesson) for result in results]


def _draft_question_from_lesson(lesson: LessonRecord) -> DraftQuestion:
    title = lesson.title or lesson.id
    topic = lesson.topic or "<missing>"

    return DraftQuestion(
        lesson_id=lesson.id,
        title=title,
        topic=topic,
        prompt=f"Spiega con parole tue: {title}",
        context_preview=_preview(lesson.text),
    )


def _preview(text: str, *, max_length: int = 240) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_length:
        return compact
    return compact[: max_length - 3] + "..."
