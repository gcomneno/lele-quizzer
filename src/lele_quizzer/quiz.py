from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from lele_quizzer.config import KnowledgeBaseConfig
from lele_quizzer.kb import LessonRecord, search_lessons


QuestionType = Literal[
    "open_explanation",
    "scenario_explanation",
    "true_false_stub",
]

QUESTION_TYPES: tuple[QuestionType, ...] = (
    "open_explanation",
    "scenario_explanation",
    "true_false_stub",
)


@dataclass(frozen=True)
class DraftQuestion:
    lesson_id: str
    title: str
    topic: str
    question_type: QuestionType
    prompt: str
    context_preview: str


def draft_questions(
    config: KnowledgeBaseConfig,
    query: str,
    *,
    limit: int = 5,
) -> list[DraftQuestion]:
    results = search_lessons(config, query, limit=limit)

    return [
        _draft_question_from_lesson(
            result.lesson,
            question_type=_question_type_for_index(index),
        )
        for index, result in enumerate(results)
    ]


def _draft_question_from_lesson(
    lesson: LessonRecord,
    *,
    question_type: QuestionType,
) -> DraftQuestion:
    title = lesson.title or lesson.id
    topic = lesson.topic or "<missing>"

    return DraftQuestion(
        lesson_id=lesson.id,
        title=title,
        topic=topic,
        question_type=question_type,
        prompt=_prompt_for_type(title, question_type),
        context_preview=_preview(lesson.text),
    )


def _question_type_for_index(index: int) -> QuestionType:
    return QUESTION_TYPES[index % len(QUESTION_TYPES)]


def _prompt_for_type(title: str, question_type: QuestionType) -> str:
    if question_type == "open_explanation":
        return f"Spiega con parole tue: {title}"

    if question_type == "scenario_explanation":
        return f"Descrivi uno scenario pratico in cui useresti: {title}"

    if question_type == "true_false_stub":
        return f"Vero o falso? Spiega la risposta: {title}"

    raise ValueError(f"Unsupported question type: {question_type}")


def _preview(text: str, *, max_length: int = 240) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_length:
        return compact
    return compact[: max_length - 3] + "..."
