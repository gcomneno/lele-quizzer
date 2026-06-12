from pathlib import Path
import json

from lele_quizzer.config import KnowledgeBaseConfig
from lele_quizzer.quiz import draft_questions


def test_draft_questions_from_search_results(tmp_path: Path) -> None:
    kb_path = tmp_path / "lessons.jsonl"
    kb_path.write_text(
        json.dumps(
            {
                "id": "git/branch",
                "text": "Un branch permette di lavorare su una linea separata.",
                "topic": "git",
                "title": "Branch e merge",
                "tags": ["git", "workflow"],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    questions = draft_questions(
        KnowledgeBaseConfig(type="lele_manager_jsonl", path=kb_path),
        "git branch",
    )

    assert len(questions) == 1
    assert questions[0].lesson_id == "git/branch"
    assert questions[0].topic == "git"
    assert questions[0].prompt == "Spiega con parole tue: Branch e merge"
    assert "branch permette" in questions[0].context_preview


def test_draft_questions_returns_empty_when_search_has_no_results(
    tmp_path: Path,
) -> None:
    kb_path = tmp_path / "lessons.jsonl"
    kb_path.write_text(
        json.dumps(
            {
                "id": "python/cache",
                "text": "La cache evita lavoro ripetuto.",
                "topic": "python",
                "title": "Caching",
                "tags": ["performance"],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    questions = draft_questions(
        KnowledgeBaseConfig(type="lele_manager_jsonl", path=kb_path),
        "kubernetes",
    )

    assert questions == []
