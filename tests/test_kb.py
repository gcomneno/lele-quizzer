from pathlib import Path
import json

from lele_quizzer.config import KnowledgeBaseConfig
from lele_quizzer.kb import inspect_knowledge_base, load_lessons


def test_load_lessons_from_lele_manager_jsonl(tmp_path: Path) -> None:
    kb_path = tmp_path / "lessons.jsonl"
    kb_path.write_text(
        json.dumps(
            {
                "id": "git/001",
                "text": "Git status mostra lo stato del repository.",
                "topic": "git",
                "title": "git status",
                "tags": ["git", "workflow"],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    config = KnowledgeBaseConfig(type="lele_manager_jsonl", path=kb_path)

    lessons = load_lessons(config)

    assert len(lessons) == 1
    assert lessons[0].id == "git/001"
    assert lessons[0].topic == "git"
    assert lessons[0].tags == ("git", "workflow")


def test_inspect_knowledge_base_counts_topics_and_tags(tmp_path: Path) -> None:
    kb_path = tmp_path / "lessons.jsonl"
    rows = [
        {"id": "1", "text": "A", "topic": "git", "tags": ["git"]},
        {"id": "2", "text": "B", "topic": "python", "tags": ["python", "testing"]},
    ]
    kb_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )

    summary = inspect_knowledge_base(
        KnowledgeBaseConfig(type="lele_manager_jsonl", path=kb_path)
    )

    assert summary.lesson_count == 2
    assert summary.topics["git"] == 1
    assert summary.topics["python"] == 1
    assert summary.tags["testing"] == 1
