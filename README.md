# LeLe Quizzer

Trivial Pursuit-style quiz layer for a LeLe Manager knowledge base.

LeLe Quizzer is a separate project from LeLe Manager. It does not own or manage the knowledge base. It reads a configured LeLe Manager JSONL export and provides terminal-based quiz commands.

## Current features

- Inspect a configured LeLe Manager JSONL knowledge base.
- Search lessons by simple local text matching.
- Draft quiz questions from relevant lessons.
- Play an interactive terminal quiz.
- Save quiz attempts locally.
- Show saved quiz attempts.

## Privacy boundary

This repository must contain only code, docs, schemas and synthetic examples.

Do not commit:

- real knowledge-base files;
- `lele-quizzer.yaml`;
- `attempts.jsonl`;
- generated indexes;
- private quiz/session data.

Use `lele-quizzer.example.yaml` as a public template and create a private local `lele-quizzer.yaml`.

## Configuration

Copy the example config:

```bash
cp lele-quizzer.example.yaml lele-quizzer.yaml
```

Then edit `lele-quizzer.yaml` so it points to your local LeLe Manager dataset, for example:

```yaml
knowledge_base:
  type: lele_manager_jsonl
  path: /home/you/.local/share/lele-manager/lessons.jsonl
```

## Commands

Inspect the configured knowledge base:

```bash
uv run lele-quizzer kb inspect
```

Search lessons:

```bash
uv run lele-quizzer kb search "git branch"
```

Draft quiz questions:

```bash
uv run lele-quizzer quiz draft "git branch"
```

Play a quiz:

```bash
uv run lele-quizzer quiz play "git branch"
```

Show saved attempts:

```bash
uv run lele-quizzer quiz attempts
```

## Development

Run checks:

```bash
uv run ruff format .
uv run ruff check .
uv run pytest -q
```
