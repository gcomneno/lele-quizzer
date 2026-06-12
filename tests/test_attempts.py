from pathlib import Path
import json

from lele_quizzer.attempts import append_attempt, load_attempts, new_attempt


def test_append_attempt_writes_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "attempts.jsonl"

    attempt = new_attempt(
        query="git branch",
        lesson_id="git/branch",
        topic="git",
        title="Branch e merge",
        prompt="Spiega con parole tue: Branch e merge",
        answer="Un branch è una linea di sviluppo separata.",
    )

    append_attempt(path, attempt)

    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    assert len(rows) == 1
    assert rows[0]["query"] == "git branch"
    assert rows[0]["lesson_id"] == "git/branch"
    assert rows[0]["answer"] == "Un branch è una linea di sviluppo separata."
    assert rows[0]["created_at"]


def test_load_attempts_returns_empty_when_file_is_missing(tmp_path: Path) -> None:
    assert load_attempts(tmp_path / "missing.jsonl") == []


def test_load_attempts_reads_last_attempts(tmp_path: Path) -> None:
    path = tmp_path / "attempts.jsonl"

    for index in range(3):
        append_attempt(
            path,
            new_attempt(
                query=f"query {index}",
                lesson_id=f"lesson-{index}",
                topic="git",
                title=f"title {index}",
                prompt=f"prompt {index}",
                answer=f"answer {index}",
            ),
        )

    attempts = load_attempts(path, limit=2)

    assert [attempt.lesson_id for attempt in attempts] == ["lesson-1", "lesson-2"]
