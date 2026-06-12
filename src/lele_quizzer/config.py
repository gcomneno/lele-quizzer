from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class KnowledgeBaseConfig:
    type: str
    path: Path
    id_column: str = "id"
    text_column: str = "text"
    topic_column: str = "topic"
    tags_column: str = "tags"
    title_column: str = "title"


@dataclass(frozen=True)
class QuizzerConfig:
    data_dir: Path
    default_question_count: int = 5
    language: str = "it"


@dataclass(frozen=True)
class RagConfig:
    backend: str = "local_text_search"
    top_k: int = 5
    min_score: float = 0.1


@dataclass(frozen=True)
class AppConfig:
    knowledge_base: KnowledgeBaseConfig
    quizzer: QuizzerConfig
    rag: RagConfig


def load_config(path: Path) -> AppConfig:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError("Config file must contain a YAML mapping.")

    kb_raw = _section(raw, "knowledge_base")
    quizzer_raw = _section(raw, "quizzer")
    rag_raw = _section(raw, "rag")

    kb_type = str(kb_raw.get("type", "")).strip()
    if not kb_type:
        raise ValueError("knowledge_base.type is required.")

    kb_path = str(kb_raw.get("path", "")).strip()
    if not kb_path:
        raise ValueError("knowledge_base.path is required.")

    return AppConfig(
        knowledge_base=KnowledgeBaseConfig(
            type=kb_type,
            path=Path(kb_path).expanduser(),
            id_column=str(kb_raw.get("id_column", "id")),
            text_column=str(kb_raw.get("text_column", "text")),
            topic_column=str(kb_raw.get("topic_column", "topic")),
            tags_column=str(kb_raw.get("tags_column", "tags")),
            title_column=str(kb_raw.get("title_column", "title")),
        ),
        quizzer=QuizzerConfig(
            data_dir=Path(
                str(quizzer_raw.get("data_dir", "~/.local/share/lele-quizzer"))
            ).expanduser(),
            default_question_count=int(quizzer_raw.get("default_question_count", 5)),
            language=str(quizzer_raw.get("language", "it")),
        ),
        rag=RagConfig(
            backend=str(rag_raw.get("backend", "local_text_search")),
            top_k=int(rag_raw.get("top_k", 5)),
            min_score=float(rag_raw.get("min_score", 0.1)),
        ),
    )


def _section(raw: dict[str, Any], name: str) -> dict[str, Any]:
    value = raw.get(name, {})
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a YAML mapping.")
    return value
