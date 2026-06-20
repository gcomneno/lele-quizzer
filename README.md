# LeLe Quizzer

Trivial Pursuit-style quiz layer for LeLe Manager knowledge bases.

LeLe Quizzer is a separate project from LeLe Manager. It does not own, import, or normalize the knowledge base. It reads a configured LeLe Manager JSONL dataset and provides terminal-based quiz commands for reviewing and practicing from that knowledge.

The goal is to turn a personal knowledge base into a small learning game: search lessons, draft questions, answer them from the terminal, save attempts locally, and inspect what needs more practice.

## Current features

- Inspect a configured LeLe Manager JSONL knowledge base.
- Search lessons with simple local text matching.
- Draft quiz questions from matching lessons.
- Generate deterministic question types:
  - `open_explanation`
  - `scenario_explanation`
  - `true_false_stub`
- Play an interactive terminal quiz.
- Save quiz attempts locally.
- Show saved quiz attempts.
- Summarize repeated topics, lesson IDs, and queries from saved attempts.

## Privacy boundary

This repository must contain only code, docs, schemas, and synthetic examples.

Do not commit:

- real knowledge-base files;
- `lele-quizzer.yaml`;
- `attempts.jsonl`;
- generated indexes;
- private quiz/session data;
- API keys or provider secrets.

Use `lele-quizzer.example.yaml` as a public template and create a private local `lele-quizzer.yaml`.

Quiz attempts are saved outside the repository, by default under the configured local data directory.

## Relationship with LeLe Manager

LeLe Manager is responsible for storing, importing, and preparing the knowledge base.

LeLe Quizzer is responsible for practicing on top of that knowledge base.

In short:

```text
LeLe Manager  -> knowledge management
LeLe Quizzer  -> quiz, practice, attempts, review
```

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

The private config file is intentionally ignored by Git.

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
uv run lele-quizzer quiz draft "git branch" --limit 3
```

Play a quiz:

```bash
uv run lele-quizzer quiz play "git branch" --limit 3
```

Show saved attempts:

```bash
uv run lele-quizzer quiz attempts --limit 10
```

Summarize repeated practice areas:

```bash
uv run lele-quizzer quiz weaknesses --limit 20 --top 10
```

## Example workflow

```bash
uv run lele-quizzer kb inspect
uv run lele-quizzer quiz draft "git branch" --limit 3
uv run lele-quizzer quiz play "git branch" --limit 3
uv run lele-quizzer quiz attempts --limit 5
uv run lele-quizzer quiz weaknesses --limit 20 --top 10
```

## Roadmap

Current roadmap direction:

- define an answer evaluation plugin boundary;
- keep the core independent from any AI provider;
- add a local deterministic/heuristic evaluator first;
- make future AI-based evaluation explicitly opt-in;
- preserve the privacy boundary for real knowledge-base content and user answers.

The project should validate local, deterministic behavior first. External AI providers can be added later through explicit configuration.

## Development

Run checks:

```bash
uv run ruff format .
uv run ruff check .
uv run pytest -q
```
