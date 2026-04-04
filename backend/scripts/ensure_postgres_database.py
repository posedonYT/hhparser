"""До миграций: ждёт PostgreSQL и создаёт целевую БД, если она ещё не существует.

Коды выхода:
  0  — всё ок
  1  — не удалось подключиться за отведённое время (транзиентная проблема)
  2  — ошибка конфигурации (неверный пароль, неверный пользователь и т.п.) — ретрай бесполезен
"""

from __future__ import annotations

import re
import sys
import time

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError

from app.core.config import get_settings

_SAFE_DB_NAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

# Фразы в сообщении об ошибке, при которых ретрай бессмысленен
_AUTH_ERROR_MARKERS = (
    "password authentication failed",
    "role",
    "does not exist",
    "pg_hba.conf",
    "no pg_hba.conf entry",
    "ident authentication failed",
)

_CONNECT_TIMEOUT_MARKERS = (
    "connection refused",
    "could not connect",
    "could not receive data",
    "the connection attempt failed",
    "server closed the connection",
    "connection reset by peer",
    "name or service not known",
    "no address associated",
)


def _is_auth_error(exc: OperationalError) -> bool:
    msg = str(exc).lower()
    return any(m in msg for m in _AUTH_ERROR_MARKERS)


def _is_transient(exc: OperationalError) -> bool:
    msg = str(exc).lower()
    return any(m in msg for m in _CONNECT_TIMEOUT_MARKERS)


def main() -> None:
    raw = get_settings().database_url
    if not raw.startswith("postgresql"):
        return

    url = make_url(raw)
    dbname = url.database
    if not dbname or not _SAFE_DB_NAME.match(dbname):
        print(
            f"[db-init] Пропуск: не PostgreSQL или некорректное имя БД ({dbname!r})",
            file=sys.stderr,
        )
        return

    admin_url = url.set(database="postgres")
    print(
        f"[db-init] Ждём PostgreSQL ({admin_url.host}:{admin_url.port}) и проверяем БД «{dbname}»…",
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
                    "  Если пароль менялся, а том остался старым — выполните:\n"
                    "    docker compose down -v && docker compose up -d --build\n"
                    f"  Детали: {exc}\n",
                    file=sys.stderr,
                )
                raise SystemExit(2) from exc

            if _is_transient(exc) or True:
                print(
                    f"[db-init] Попытка {attempt}/60: PostgreSQL ещё не готов ({exc!r}). "
                    "Ждём 2 сек…",
                    flush=True,
                )
                time.sleep(2)

    print(
        f"[db-init] Не удалось подключиться к PostgreSQL за 60 попыток.\n"
        f"  Последняя ошибка: {last_error}\n",
        file=sys.stderr,
    )
    raise SystemExit(1) from last_error


if __name__ == "__main__":
    main()
