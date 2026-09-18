# job-status-found backend

FastAPI service managed with uv (Python 3.14).

```shell
# install runtime and dev tools
uv sync
uv run uvicorn job_status_found.main:app --reload
```

## Checks

```shell
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest --cov
```

Docstring rules live in [AGENTS.md](AGENTS.md).

Settings are read from `JSF_`-prefixed environment variables or `.env`
(see `src/job_status_found/app/settings.py`).

Browsers may call the API only from origins matching
`JSF_CORS_ALLOW_ORIGIN_REGEX`. The default allows any `localhost` or
`127.0.0.1` port, which covers `flutter run -d chrome`.
