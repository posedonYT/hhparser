"""До миграций: ждёт PostgreSQL и создаёт целевую БД, если она ещё не существует.

Скрипт намеренно НЕ импортирует ничего из пакета «app», чтобы работать
при любом sys.path (в том числе когда Python запущен из директории scripts/).

Коды выхода:
  0 — ОК
  1 — не удалось подключиться за отведённое время (транзиентная ошибка)
  2 — ошибка конфигурации (неверный пароль / пользователь) — ретрай бесполезен
"""

from __future__ import annotations

import os
import re
import sys
import time
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError

_SAFE_DB_NAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

_AUTH_ERROR_MARKERS = (
    "password authentication failed",
    "role",
    "does not exist",
    "pg_hba.conf",
    "no pg_hba.conf entry",
    "ident authentication failed",
)


def _get_database_url() -> str:
    """Строит URL из DATABASE_URL или POSTGRES_* переменных окружения."""
    direct = os.environ.get("DATABASE_URL", "").strip()
    if direct:
        return direct
    user = quote_plus(os.environ.get("POSTGRES_USER", "postgres"))
    password = quote_plus(os.environ.get("POSTGRES_PASSWORD", "postgres"))
    host = os.environ.get("POSTGRES_HOST", "postgres")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db = os.environ.get("POSTGRES_DB", "hh_analytics")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


def _is_auth_error(exc: OperationalError) -> bool:
    msg = str(exc).lower()
    return any(m in msg for m in _AUTH_ERROR_MARKERS)


def main() -> None:
    raw = _get_database_url()
    if not raw.startswith("postgresql"):
        print("[db-init] Не PostgreSQL — пропуск.", flush=True)
        return

    url = make_url(raw)
    dbname = url.database
    if not dbname or not _SAFE_DB_NAME.match(dbname):
        print(f"[db-init] Некорректное имя БД ({dbname!r}) — пропуск.", file=sys.stderr)
        return

    admin_url = url.set(database="postgres")
    print(
        f"[db-init] Ждём PostgreSQL ({admin_url.host}:{admin_url.port}), проверяем БД «{dbname}»…",
        flush=True,
    )

    last_error: OperationalError | None = None

    for attempt in range(1, 61):
        try:
            engine = create_engine(
                admin_url,
                isolation_level="AUTOCOMMIT",
                pool_pre_ping=True,
                connect_args={"connect_timeout": 5},
            )
            with engine.connect() as conn:
                exists = conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :n"),
                    {"n": dbname},
                ).scalar()
                if exists != 1:
                    print(f"[db-init] Создаём БД «{dbname}»…", flush=True)
                    conn.execute(text(f"CREATE DATABASE {dbname}"))
                    print(f"[db-init] БД «{dbname}» создана.", flush=True)
                else:
                    print(f"[db-init] БД «{dbname}» уже существует.", flush=True)
            engine.dispose()
            return

        except OperationalError as exc:
            last_error = exc

            if _is_auth_error(exc):
                print(
                    "\n[db-init] ОШИБКА АУТЕНТИФИКАЦИИ — ретрай бесполезен.\n"
                    "  Проверьте POSTGRES_USER / POSTGRES_PASSWORD.\n"
                    "  Если пароль менялся при существующем томе — выполните:\n"
                    "    docker compose down -v && docker compose up -d --build\n"
                    f"  Детали: {exc}\n",
                    file=sys.stderr,
                )
                raise SystemExit(2) from exc

            print(
                f"[db-init] Попытка {attempt}/60: сервер не готов — {type(exc).__name__}. Ждём 2с…",
                flush=True,
            )
            time.sleep(2)

    print(
        f"[db-init] Не удалось подключиться за 60 попыток. Последняя ошибка: {last_error}",
        file=sys.stderr,
    )
    raise SystemExit(1) from last_error


if __name__ == "__main__":
    main()
