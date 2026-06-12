from pathlib import Path

from lele_quizzer.config import load_config


def test_load_config_reads_knowledge_base_path(tmp_path: Path) -> None:
    config_path = tmp_path / "lele-quizzer.yaml"
    kb_path = tmp_path / "lessons.jsonl"

    config_path.write_text(
        f"""
knowledge_base:
  type: lele_manager_jsonl
  path: {kb_path}

quizzer:
  data_dir: {tmp_path / "quizzer-data"}
  default_question_count: 7
  language: it

rag:
  backend: local_text_search
  top_k: 3
  min_score: 0.2
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.knowledge_base.type == "lele_manager_jsonl"
    assert config.knowledge_base.path == kb_path
    assert config.quizzer.default_question_count == 7
    assert config.rag.top_k == 3
